from __future__ import annotations

import asyncio
import difflib
import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from backend.compiler.service import compile_source
from backend.projects.store import ProjectConflict, ProjectNotFound, ProjectStore
from backend.runtime.runner import OciRunner, RunnerBusy, RunnerUnavailable
from backend.test_service.differential import compare_targets
from backend.test_service.official import official_case_requests, official_data
from backend.test_service.reporting import report_markdown, report_pdf

from .exports import diagnostics_text
from .schemas import (
    ExportRequest,
    ProjectCreateRequest,
    ProjectUpdateRequest,
    RunRequest,
    SourceRequest,
    TestRunRequest,
    TranslateRequest,
)

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.environ.get("PSEUDO_STUDIO_DATA_DIR", ROOT / "data")).expanduser().resolve()
DATABASE_PATH = Path(os.environ.get("PSEUDO_STUDIO_DB_PATH", DATA_DIR / "projects.sqlite3"))
MAX_REQUEST_BYTES = 1_048_576
RATE_LIMIT_PER_MINUTE = 120
ALLOWED_ORIGINS = tuple(
    item.strip()
    for item in os.environ.get("PSEUDO_STUDIO_ALLOWED_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173").split(
        ","
    )
    if item.strip()
)
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"), format="%(message)s")
logger = logging.getLogger("pseudo_studio.api")


class ExportRegistry:
    MIME = {
        ".psc": "text/plain; charset=utf-8",
        ".py": "text/x-python; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".txt": "text/plain; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".md": "text/markdown; charset=utf-8",
        ".pdf": "application/pdf",
    }
    EXTENSIONS = {
        "source": ".psc",
        "python": ".py",
        "javascript": ".js",
        "python-txt": ".txt",
        "javascript-txt": ".txt",
        "tokens": ".json",
        "ast": ".json",
        "symbols": ".json",
        "diagnostics": ".json",
        "diagnostics-txt": ".txt",
        "phases": ".json",
        "report-json": ".json",
        "report-markdown": ".md",
        "report-pdf": ".pdf",
    }

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.entries: dict[str, tuple[Path, str, str]] = {}

    def create(self, kind: str, content: bytes) -> dict[str, str]:
        export_id = uuid.uuid4().hex
        extension = self.EXTENSIONS[kind]
        path = self.root / f"{export_id}{extension}"
        filename = f"pseudo-studio-{kind}-{export_id[:8]}{extension}"
        mime = self.MIME[extension]
        content_pending = path.with_name(f".{path.name}.pending")
        metadata_path = self.root / f"{export_id}.meta.json"
        metadata_pending = metadata_path.with_name(f".{metadata_path.name}.pending")
        content_pending.write_bytes(content)
        content_pending.replace(path)
        metadata_pending.write_text(json.dumps({"kind": kind}, separators=(",", ":")), encoding="utf-8")
        metadata_pending.replace(metadata_path)
        self.entries[export_id] = (path, filename, mime)
        return {"id": export_id, "url": f"/api/v1/exports/{export_id}", "filename": filename, "mime_type": mime}

    def get(self, export_id: str) -> tuple[Path, str, str] | None:
        if not (len(export_id) == 32 and all(char in "0123456789abcdef" for char in export_id)):
            return None
        entry = self.entries.get(export_id)
        if entry is not None and entry[0].is_file():
            return entry
        metadata_path = self.root / f"{export_id}.meta.json"
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        kind = metadata.get("kind") if isinstance(metadata, dict) else None
        if kind not in self.EXTENSIONS:
            return None
        extension = self.EXTENSIONS[kind]
        path = self.root / f"{export_id}{extension}"
        if not path.is_file():
            return None
        filename = f"pseudo-studio-{kind}-{export_id[:8]}{extension}"
        mime = self.MIME[extension]
        entry = (path, filename, mime)
        self.entries[export_id] = entry
        return entry


class RequestBodyLimitMiddleware:
    """Bound request bodies even when a client omits Content-Length and streams chunks."""

    def __init__(self, app: ASGIApp, *, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("method") in {"GET", "HEAD", "OPTIONS"}:
            await self.app(scope, receive, send)
            return
        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        raw_length = headers.get(b"content-length", b"")
        if raw_length.isdigit() and int(raw_length) > self.max_bytes:
            await self._reject(scope, send)
            return
        messages: list[Message] = []
        size = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            messages.append(message)
            size += len(message.get("body", b""))
            if size > self.max_bytes:
                await self._reject(scope, send)
                return
            if not message.get("more_body", False):
                break
        index = 0

        async def replay() -> Message:
            nonlocal index
            if index < len(messages):
                message = messages[index]
                index += 1
                return message
            return await receive()

        await self.app(scope, replay, send)

    @staticmethod
    async def _reject(scope: Scope, send: Send) -> None:
        request_headers = {key.lower(): value for key, value in scope.get("headers", [])}
        request_id = request_headers.get(b"x-request-id", b"").decode("ascii", errors="ignore")
        body = json.dumps({"error": {"code": "REQUEST_TOO_LARGE", "request_id": request_id or None}}).encode()
        headers = [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())]
        await send({"type": "http.response.start", "status": 413, "headers": headers})
        await send({"type": "http.response.body", "body": body})


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _compile_error(result: Any) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "code": "COMPILE_INVALID",
            "message": "La fuente contiene errores y no se generó ningún artefacto.",
            "diagnostics": [item.to_dict() for item in result.diagnostics],
            "source_hash": result.source_hash,
        },
    )


def create_app(*, store: ProjectStore | None = None, runner: OciRunner | None = None) -> FastAPI:
    runtime_runner = runner or OciRunner()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.store = store or ProjectStore(DATABASE_PATH)
        app.state.runner = runtime_runner
        app.state.sandbox_verification = await asyncio.to_thread(runtime_runner.verify_controls)
        app.state.exports = ExportRegistry(DATA_DIR / "exports")
        app.state.reports = {}
        yield

    app = FastAPI(
        title="Pseudo / Studio API",
        version="1.0.0",
        description="API local para compilar y ejecutar pseudocódigo en runtimes aislados.",
        openapi_url="/api/v1/openapi.json",
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(ALLOWED_ORIGINS),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )
    app.add_middleware(RequestBodyLimitMiddleware, max_bytes=MAX_REQUEST_BYTES)
    request_times: dict[str, list[float]] = {}

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("x-request-id")
        if not request_id or len(request_id) > 80 or not all(char.isalnum() or char in "-_" for char in request_id):
            request_id = uuid.uuid4().hex
        request.state.request_id = request_id
        if request.method in {"POST", "PUT", "DELETE"} and request.url.path != "/api/v1/health":
            client_key = request.client.host if request.client else "local"
            now = time.monotonic()
            recent = [stamp for stamp in request_times.get(client_key, []) if now - stamp < 60]
            if len(recent) >= RATE_LIMIT_PER_MINUTE:
                request_times[client_key] = recent
                response = JSONResponse(
                    status_code=429, content={"detail": {"code": "RATE_LIMITED", "retry_after_seconds": 60}}
                )
                response.headers["Retry-After"] = "60"
                response.headers["X-Request-ID"] = request_id
                return response
            recent.append(now)
            request_times[client_key] = recent
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > MAX_REQUEST_BYTES:
            response = JSONResponse(
                status_code=413, content={"error": {"code": "REQUEST_TOO_LARGE", "request_id": request_id}}
            )
        else:
            started = time.perf_counter()
            response = await call_next(request)
            logger.info(
                json.dumps(
                    {
                        "event": "http_request",
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "status": response.status_code,
                        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                    }
                )
            )
        response.headers["X-Request-ID"] = request_id
        return response

    def require_sandbox() -> dict[str, Any]:
        status = app.state.runner.status()
        verified = app.state.sandbox_verification.get("available", False)
        if not status.get("available") or not verified:
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "RUN_SANDBOX_UNAVAILABLE",
                    "message": "La ejecución está deshabilitada porque el aislamiento OCI no pasó su verificación.",
                    "sandbox": status,
                    "verification": app.state.sandbox_verification,
                },
            )
        return status

    @app.get("/api/v1/health")
    async def health() -> dict[str, Any]:
        try:
            database = app.state.store.health()
        except Exception:
            database = False
        sandbox = app.state.runner.status()
        verification = app.state.sandbox_verification
        ready = database and sandbox.get("available", False) and verification.get("available", False)
        return {
            "status": "ready" if ready else "degraded",
            "components": {
                "api": {"available": True, "version": app.version},
                "database": {"available": database, "engine": "sqlite"},
                "compiler": {
                    "available": True,
                    "version": compile_source("Inicio\nFin\n", targets=()).compiler_version,
                },
                "sandbox": sandbox,
                "sandbox_verification": verification,
            },
        }

    @app.post("/api/v1/analyze")
    async def analyze_source(payload: SourceRequest) -> dict[str, Any]:
        return compile_source(payload.source, targets=()).to_dict(include_code=False)

    @app.post("/api/v1/translate")
    async def translate(payload: TranslateRequest) -> dict[str, Any]:
        targets = tuple(dict.fromkeys(payload.targets))
        result = compile_source(payload.source, targets=targets)
        if not result.translatable:
            raise _compile_error(result)
        return result.to_dict(include_code=True)

    @app.post("/api/v1/run")
    async def run(payload: RunRequest) -> dict[str, Any]:
        require_sandbox()
        if payload.project_id:
            try:
                app.state.store.get_project(payload.project_id)
            except ProjectNotFound as error:
                raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND"}) from error
        result = compile_source(payload.source, targets=(payload.target,))
        if not result.translatable:
            raise _compile_error(result)
        artifact = result.artifacts[payload.target]
        run_id = payload.run_id or uuid.uuid4().hex
        try:
            execution = await asyncio.to_thread(
                app.state.runner.run_batch,
                payload.target,
                artifact.source,
                payload.inputs.values,
                result.source_hash,
                artifact.artifact_hash,
                run_id,
            )
        except RunnerUnavailable as error:
            raise HTTPException(
                status_code=503, detail={"code": "RUN_SANDBOX_UNAVAILABLE", "details": error.details}
            ) from error
        except RunnerBusy as error:
            raise HTTPException(status_code=429, detail={"code": str(error)}) from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail={"code": "RUN_INPUT_INVALID", "message": str(error)}) from error
        app.state.store.record_run(execution.to_dict(), payload.project_id)
        return execution.to_dict()

    @app.post("/api/v1/runs/{run_id}/cancel")
    async def cancel_run(run_id: str) -> dict[str, Any]:
        if not all(char.isalnum() or char in "-_" for char in run_id):
            raise HTTPException(status_code=400, detail={"code": "RUN_ID_INVALID"})
        cancelled = await asyncio.to_thread(app.state.runner.cancel, run_id)
        if not cancelled:
            raise HTTPException(status_code=404, detail={"code": "RUN_NOT_ACTIVE"})
        return {"run_id": run_id, "status": "cancellation_requested"}

    @app.get("/api/v1/examples")
    async def examples() -> dict[str, Any]:
        data = official_data()
        titles = {
            "A": "Operaciones aritméticas y agrupación",
            "B": "Condicional anidado con operadores lógicos",
            "C": "Para y acumuladores",
            "D": "Arreglos con índice 1-based",
            "E": "Funciones con parámetros y retorno",
        }
        return {
            "examples": [
                {
                    "id": program,
                    "title": titles[program],
                    "source_path": path,
                    "case_count": sum(1 for case in data["cases"] if case["program"] == program),
                }
                for program, path in data["source_files"].items()
            ]
        }

    @app.get("/api/v1/grammar", response_class=PlainTextResponse)
    async def grammar() -> str:
        grammar_path = ROOT / "docs/gramatica.ebnf"
        if not grammar_path.is_file():
            raise HTTPException(status_code=503, detail={"code": "GRAMMAR_UNAVAILABLE"})
        return grammar_path.read_text(encoding="utf-8")

    @app.get("/api/v1/examples/{example_id}")
    async def example(example_id: str) -> dict[str, Any]:
        if example_id not in "ABCDE" or len(example_id) != 1:
            raise HTTPException(status_code=404, detail={"code": "EXAMPLE_NOT_FOUND"})
        data = official_data()
        source = (ROOT / data["source_files"][example_id]).read_text(encoding="utf-8")
        return {
            "id": example_id,
            "source": source,
            "cases": official_case_requests(example_id),
            "authority": data["authority"],
        }

    @app.post("/api/v1/tests/run")
    async def run_tests(payload: TestRunRequest) -> dict[str, Any]:
        require_sandbox()
        if payload.project_id:
            try:
                app.state.store.get_project(payload.project_id)
            except ProjectNotFound as error:
                raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND"}) from error
        if payload.example_id:
            data = official_data()
            source = (ROOT / data["source_files"][payload.example_id]).read_text(encoding="utf-8")
            cases = official_case_requests(payload.example_id)
        else:
            source = payload.source or ""
            cases = [case.model_dump() for case in payload.test_cases]
        compiled = compile_source(source)
        if not compiled.translatable:
            raise _compile_error(compiled)
        runs = []
        for case in cases:
            for target in ("python", "javascript"):
                artifact = compiled.artifacts[target]
                try:
                    execution = await asyncio.to_thread(
                        app.state.runner.run_batch,
                        target,
                        artifact.source,
                        case["inputs"],
                        compiled.source_hash,
                        artifact.artifact_hash,
                    )
                except RunnerBusy as error:
                    raise HTTPException(status_code=429, detail={"code": str(error)}) from error
                actual = execution.stdout
                passed = (
                    execution.status == "completed"
                    and execution.exit_code == 0
                    and actual == case["expected_stdout"]
                    and not execution.stderr
                )
                record = {
                    "case_id": case["id"],
                    "target": target,
                    "inputs": case["inputs"],
                    "expected_stdout": case["expected_stdout"],
                    "actual_stdout": actual,
                    "stderr": execution.stderr,
                    "status": execution.status,
                    "exit_code": execution.exit_code,
                    "duration_ms": execution.duration_ms,
                    "source_hash": execution.source_hash,
                    "artifact_hash": execution.artifact_hash,
                    "runtime_version": execution.runtime_version,
                    "error_code": execution.error_code,
                    "passed": passed,
                    "diff": ""
                    if actual == case["expected_stdout"]
                    else "\n".join(
                        difflib.unified_diff(
                            case["expected_stdout"].splitlines(),
                            actual.splitlines(),
                            fromfile="expected",
                            tofile="actual",
                            lineterm="",
                        )
                    ),
                }
                runs.append(record)
                app.state.store.record_run(execution.to_dict(), payload.project_id)
        report_id = uuid.uuid4().hex
        passed_count = sum(1 for item in runs if item["passed"])
        report = {
            "report_id": report_id,
            "generated_at": _iso_now(),
            "source_hash": compiled.source_hash,
            "compiler_version": compiled.compiler_version,
            "total": len(runs),
            "passed": passed_count,
            "failed": len(runs) - passed_count,
            "runs": runs,
            "comparisons": compare_targets(runs),
        }
        app.state.reports[report_id] = report
        while len(app.state.reports) > 20:
            del app.state.reports[next(iter(app.state.reports))]
        return report

    @app.get("/api/v1/projects")
    async def list_projects() -> dict[str, Any]:
        return {"projects": app.state.store.list_projects()}

    @app.post("/api/v1/projects", status_code=201)
    async def create_project(payload: ProjectCreateRequest) -> dict[str, Any]:
        return app.state.store.create_project(payload.name, payload.source)

    @app.get("/api/v1/projects/{project_id}")
    async def get_project(project_id: str) -> dict[str, Any]:
        try:
            return app.state.store.get_project(project_id)
        except ProjectNotFound as error:
            raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND"}) from error

    @app.put("/api/v1/projects/{project_id}")
    async def update_project(project_id: str, payload: ProjectUpdateRequest) -> dict[str, Any]:
        try:
            return app.state.store.update_project(
                project_id,
                payload.version,
                name=payload.name,
                source=payload.source,
            )
        except ProjectNotFound as error:
            raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND"}) from error
        except ProjectConflict as error:
            raise HTTPException(
                status_code=409, detail={"code": "PROJECT_VERSION_CONFLICT", "message": str(error)}
            ) from error

    @app.post("/api/v1/projects/{project_id}/duplicate", status_code=201)
    async def duplicate_project(project_id: str) -> dict[str, Any]:
        try:
            return app.state.store.duplicate_project(project_id)
        except ProjectNotFound as error:
            raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND"}) from error

    @app.delete("/api/v1/projects/{project_id}", status_code=204)
    async def delete_project(project_id: str) -> None:
        try:
            app.state.store.delete_project(project_id)
        except ProjectNotFound as error:
            raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND"}) from error

    @app.get("/api/v1/projects/{project_id}/runs")
    async def project_runs(project_id: str) -> dict[str, Any]:
        try:
            app.state.store.get_project(project_id)
        except ProjectNotFound as error:
            raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND"}) from error
        return {"runs": [item for item in app.state.store.list_runs() if item["project_id"] == project_id]}

    @app.post("/api/v1/exports", status_code=201)
    async def create_export(payload: ExportRequest) -> dict[str, str]:
        kind = payload.kind
        if kind.startswith("report-"):
            report = app.state.reports.get(payload.report_id or "")
            if report is None:
                raise HTTPException(status_code=404, detail={"code": "TEST_REPORT_NOT_FOUND"})
            if kind == "report-json":
                content = json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")
            elif kind == "report-markdown":
                content = report_markdown(report).encode("utf-8")
            else:
                content = report_pdf(report)
        elif kind == "source":
            content = (payload.source or "").encode("utf-8")
        else:
            target = {"python-txt": "python", "javascript-txt": "javascript"}.get(kind, kind)
            result = compile_source(
                payload.source or "", targets=(target,) if target in {"python", "javascript"} else ()
            )
            if kind == "tokens":
                content = json.dumps(result.tokens, ensure_ascii=False, indent=2).encode("utf-8")
            elif kind == "diagnostics":
                content = json.dumps(
                    [item.to_dict() for item in result.diagnostics], ensure_ascii=False, indent=2
                ).encode("utf-8")
            elif kind == "diagnostics-txt":
                content = diagnostics_text(result).encode("utf-8")
            elif kind == "phases":
                content = json.dumps(result.phases, ensure_ascii=False, indent=2).encode("utf-8")
            elif not result.translatable:
                raise _compile_error(result)
            elif kind in {"python", "javascript", "python-txt", "javascript-txt"}:
                content = result.artifacts[target].source.encode("utf-8")
            elif kind == "ast":
                content = json.dumps(result.ast, ensure_ascii=False, indent=2).encode("utf-8")
            elif kind == "symbols":
                content = json.dumps(result.symbols, ensure_ascii=False, indent=2).encode("utf-8")
        return app.state.exports.create(kind, content)

    @app.get("/api/v1/exports/{export_id}")
    async def download_export(export_id: str):
        entry = app.state.exports.get(export_id)
        if entry is None or not entry[0].is_file():
            raise HTTPException(status_code=404, detail={"code": "EXPORT_NOT_FOUND"})
        path, filename, mime = entry
        return FileResponse(path, filename=filename, media_type=mime)

    @app.websocket("/api/v1/run/interactive")
    async def interactive_run(websocket: WebSocket) -> None:
        origin = websocket.headers.get("origin")
        if origin and origin not in ALLOWED_ORIGINS:
            await websocket.close(code=4403, reason="Origin no permitido")
            return
        await websocket.accept()
        session = None
        receive_task: asyncio.Task[Any] | None = None
        closed = False
        send_lock = asyncio.Lock()
        output_bytes = 0

        async def send(event: dict[str, Any]) -> None:
            async with send_lock:
                await websocket.send_json(event)

        try:
            initial = await websocket.receive_json()
            if not isinstance(initial, dict) or initial.get("type") != "start":
                await send(
                    {
                        "event": "error",
                        "code": "WS_PROTOCOL_ERROR",
                        "message": "El primer mensaje debe iniciar una ejecución.",
                    }
                )
                await websocket.close(code=4400)
                return
            target = initial.get("target")
            source = initial.get("source")
            if target not in {"python", "javascript"} or not isinstance(source, str):
                await send({"event": "error", "code": "WS_REQUEST_INVALID"})
                await websocket.close(code=4400)
                return
            require_sandbox()
            compiled = compile_source(source, targets=(target,))
            if not compiled.translatable:
                await send(
                    {
                        "event": "error",
                        "code": "COMPILE_INVALID",
                        "diagnostics": [item.to_dict() for item in compiled.diagnostics],
                    }
                )
                await websocket.close(code=4400)
                return
            artifact = compiled.artifacts[target]
            session = await app.state.runner.start_interactive(
                target, artifact.source, compiled.source_hash, artifact.artifact_hash
            )
            await send(
                {
                    "event": "started",
                    "run_id": session.run_id,
                    "target": target,
                    "source_hash": compiled.source_hash,
                    "artifact_hash": artifact.artifact_hash,
                }
            )
            active_timeout_deadline = time.monotonic() + app.state.runner.timeout_seconds
            input_wait_started: float | None = None

            async def pump_stdout() -> None:
                nonlocal output_bytes
                assert session.process.stdout
                while chunk := await session.process.stdout.read(4096):
                    output_bytes += len(chunk)
                    session.stdout.extend(chunk)
                    if output_bytes > app.state.runner.output_limit:
                        session.forced_status = ("output_limited", "RUN_OUTPUT_LIMIT")
                        await asyncio.to_thread(app.state.runner.cancel, session.run_id)
                        return
                    await send({"event": "stdout", "data": chunk.decode("utf-8", errors="replace")})

            async def pump_stderr() -> None:
                nonlocal output_bytes, input_wait_started
                assert session.process.stderr
                buffer = bytearray()

                async def handle_line(line: bytes) -> None:
                    nonlocal output_bytes, input_wait_started
                    if line.startswith(b"\x1ePS_INPUT:"):
                        kind = line[len(b"\x1ePS_INPUT:") :].decode("ascii", errors="replace").strip()
                        if input_wait_started is None:
                            input_wait_started = time.monotonic()
                        await send({"event": "input_requested", "input_type": kind})
                    else:
                        output_bytes += len(line) + 1
                        session.stderr.extend(line + b"\n")
                        if output_bytes > app.state.runner.output_limit:
                            session.forced_status = ("output_limited", "RUN_OUTPUT_LIMIT")
                            await asyncio.to_thread(app.state.runner.cancel, session.run_id)
                        else:
                            await send({"event": "stderr", "data": line.decode("utf-8", errors="replace") + "\n"})

                while chunk := await session.process.stderr.read(4096):
                    buffer.extend(chunk)
                    while b"\n" in buffer:
                        line, _, remaining = buffer.partition(b"\n")
                        buffer = bytearray(remaining)
                        await handle_line(bytes(line))
                if buffer:
                    await handle_line(bytes(buffer))

            stdout_task = asyncio.create_task(pump_stdout())
            stderr_task = asyncio.create_task(pump_stderr())
            receive_task = asyncio.create_task(websocket.receive_json())
            while session.process.returncode is None:
                if input_wait_started is None and time.monotonic() > active_timeout_deadline:
                    session.forced_status = ("timed_out", "RUN_TIMEOUT")
                    await asyncio.to_thread(app.state.runner.cancel, session.run_id)
                    break
                done, _ = await asyncio.wait({receive_task}, timeout=0.1)
                if not done:
                    continue
                message = receive_task.result()
                receive_task = asyncio.create_task(websocket.receive_json())
                message_type = message.get("type") if isinstance(message, dict) else None
                if message_type == "input" and isinstance(message.get("value"), str):
                    try:
                        await app.state.runner.send_interactive_input(session, message["value"])
                        if input_wait_started is not None:
                            active_timeout_deadline += time.monotonic() - input_wait_started
                            input_wait_started = None
                    except ValueError as error:
                        await send({"event": "error", "code": "RUN_INPUT_INVALID", "message": str(error)})
                    except RuntimeError:
                        await send({"event": "error", "code": "RUN_SESSION_CLOSED"})
                elif message_type == "cancel":
                    await asyncio.to_thread(app.state.runner.cancel, session.run_id)
                    break
                else:
                    await send({"event": "error", "code": "WS_PROTOCOL_ERROR"})
            await session.process.wait()
            await asyncio.gather(stdout_task, stderr_task, return_exceptions=True)
            if receive_task is not None and not receive_task.done():
                receive_task.cancel()
                await asyncio.gather(receive_task, return_exceptions=True)
            execution = await app.state.runner.finish_interactive(session)
            app.state.store.record_run(execution.to_dict())
            await send({"event": "exited", **execution.to_dict()})
        except WebSocketDisconnect:
            closed = True
            if session:
                await asyncio.to_thread(app.state.runner.cancel, session.run_id)
                await session.process.wait()
                await app.state.runner.finish_interactive(session, cancelled=True)
        except HTTPException as error:
            await send(
                {
                    "event": "error",
                    "code": error.detail.get("code", "RUN_UNAVAILABLE")
                    if isinstance(error.detail, dict)
                    else "RUN_UNAVAILABLE",
                    "detail": error.detail,
                }
            )
            await websocket.close(code=4403 if error.status_code == 503 else 4400)
        except RunnerBusy as error:
            await send({"event": "error", "code": str(error), "message": str(error)})
            await websocket.close(code=4429)
        except (RunnerUnavailable, ValueError) as error:
            await send({"event": "error", "code": "RUN_SANDBOX_UNAVAILABLE", "message": str(error)})
            await websocket.close(code=4503)
        finally:
            if receive_task is not None and not receive_task.done():
                receive_task.cancel()
                await asyncio.gather(receive_task, return_exceptions=True)
            if session and session.process.returncode is None:
                await asyncio.to_thread(app.state.runner.cancel, session.run_id)
                await session.process.wait()
                await app.state.runner.finish_interactive(session, cancelled=True)
            if not closed and websocket.application_state.name == "CONNECTED":
                await websocket.close()

    return app


app = create_app()
