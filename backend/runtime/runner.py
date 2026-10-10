"""Bounded Docker execution in the Docker Desktop WSL2 VM or a rootless engine."""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
import selectors
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "sandbox/runtime-images.json"


@dataclass(slots=True)
class RunResult:
    run_id: str
    target: str
    status: str
    stdout: str
    stderr: str
    exit_code: int | None
    duration_ms: float
    error_code: str | None
    source_hash: str
    artifact_hash: str
    runtime_version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "target": self.target,
            "status": self.status,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "duration_ms": self.duration_ms,
            "error_code": self.error_code,
            "source_hash": self.source_hash,
            "artifact_hash": self.artifact_hash,
            "runtime_version": self.runtime_version,
        }


class RunnerUnavailable(RuntimeError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


class RunnerBusy(RuntimeError):
    pass


@dataclass(slots=True)
class InteractiveSession:
    run_id: str
    container_name: str
    target: str
    process: asyncio.subprocess.Process
    temp_directory: tempfile.TemporaryDirectory
    started: float
    source_hash: str
    artifact_hash: str
    stdout: bytearray
    stderr: bytearray
    forced_status: tuple[str, str] | None = None
    slot_held: bool = True


class OciRunner:
    def __init__(
        self,
        *,
        timeout_seconds: float | None = None,
        output_limit: int | None = None,
        max_concurrent_runs: int | None = None,
        memory_mb: int | None = None,
        cpu_limit: float | None = None,
        pids_limit: int | None = None,
    ) -> None:
        self.timeout_seconds = self._float_setting(
            "PSEUDO_STUDIO_RUN_TIMEOUT_SECONDS",
            timeout_seconds,
            5.0,
            0.1,
            300.0,
        )
        self.output_limit = self._int_setting(
            "PSEUDO_STUDIO_OUTPUT_LIMIT_BYTES", output_limit, 1_048_576, 1024, 16_777_216
        )
        self.max_concurrent_runs = self._int_setting("PSEUDO_STUDIO_MAX_CONCURRENT_RUNS", max_concurrent_runs, 4, 1, 32)
        self.memory_mb = self._int_setting("PSEUDO_STUDIO_MEMORY_MB", memory_mb, 256, 64, 4096)
        self.cpu_limit = self._float_setting("PSEUDO_STUDIO_CPU_LIMIT", cpu_limit, 1.0, 0.1, 16.0)
        self.pids_limit = self._int_setting("PSEUDO_STUDIO_PIDS_LIMIT", pids_limit, 64, 16, 1024)
        self._run_slots = threading.BoundedSemaphore(self.max_concurrent_runs)
        self._manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self._images = {name: image["reference"] for name, image in self._manifest["images"].items()}
        self._active: dict[str, str] = {}
        self._cancelled: set[str] = set()
        self._active_lock = threading.Lock()
        self._engine = os.environ.get("PSEUDO_STUDIO_OCI_ENGINE", "docker")
        self._seccomp = ROOT / self._manifest["seccomp"]["file"]

    @staticmethod
    def _int_setting(name: str, explicit: int | None, default: int, minimum: int, maximum: int) -> int:
        raw = explicit if explicit is not None else int(os.environ.get(name, default))
        if not minimum <= raw <= maximum:
            raise ValueError(f"{name} debe estar entre {minimum} y {maximum}.")
        return raw

    @staticmethod
    def _float_setting(name: str, explicit: float | None, default: float, minimum: float, maximum: float) -> float:
        raw = explicit if explicit is not None else float(os.environ.get(name, default))
        if not math.isfinite(raw) or not minimum <= raw <= maximum:
            raise ValueError(f"{name} debe estar entre {minimum} y {maximum}.")
        return raw

    @staticmethod
    def _isolation_boundary(details: dict[str, Any]) -> str | None:
        security = details.get("SecurityOptions", [])
        names = " ".join(str(item) for item in security).casefold()
        if "rootless" in names:
            return "rootless-oci"
        operating_system = str(details.get("OperatingSystem", "")).casefold()
        kernel = str(details.get("KernelVersion", "")).casefold()
        if "docker desktop" in operating_system and ("linuxkit" in kernel or "microsoft-standard-wsl2" in kernel):
            return "docker-desktop-vm"
        return None

    def status(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "available": False,
            "engine": self._engine,
            "engine_ready": False,
            "isolation_boundary": None,
            "seccomp": False,
            "images": {},
            "runtimes": {},
            "quotas": {
                "timeout_seconds": self.timeout_seconds,
                "output_bytes": self.output_limit,
                "concurrent_runs": self.max_concurrent_runs,
                "memory_mb": self.memory_mb,
                "cpu_limit": self.cpu_limit,
                "pids_limit": self.pids_limit,
            },
            "reasons": [],
        }
        if not shutil.which(self._engine):
            result["reasons"].append(f"No se encontró el ejecutable OCI '{self._engine}'.")
            return result
        try:
            info = subprocess.run(
                [self._engine, "info", "--format", "{{json .}}"],
                capture_output=True,
                text=True,
                timeout=4,
                check=False,
            )
            if info.returncode != 0:
                result["reasons"].append(info.stderr.strip() or "El engine OCI no responde.")
                return result
            details = json.loads(info.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as error:
            result["reasons"].append(f"No se pudo consultar el engine OCI: {error}.")
            return result
        result["engine_ready"] = True
        result["isolation_boundary"] = self._isolation_boundary(details)
        if not result["isolation_boundary"]:
            result["reasons"].append("El engine no declara rootless ni una VM Docker Desktop/WSL2 comprobable.")

        try:
            seccomp_bytes = self._seccomp.read_bytes()
            profile = json.loads(seccomp_bytes)
            digest = hashlib.sha256(seccomp_bytes).hexdigest()
            result["seccomp"] = (
                digest == self._manifest["seccomp"]["sha256"]
                and profile.get("defaultAction") == "SCMP_ACT_ERRNO"
                and bool(profile.get("syscalls"))
            )
        except (OSError, json.JSONDecodeError):
            result["seccomp"] = False
        if not result["seccomp"]:
            result["reasons"].append("El perfil seccomp fijado falta, no es válido o su SHA-256 no coincide.")

        for target, reference in self._images.items():
            try:
                image = subprocess.run(
                    [self._engine, "image", "inspect", reference, "--format", "{{.Id}}"],
                    capture_output=True,
                    text=True,
                    timeout=4,
                    check=False,
                )
            except (subprocess.TimeoutExpired, OSError):
                image = None
            present = image is not None and image.returncode == 0 and bool(image.stdout.strip())
            result["images"][target] = present
            if not present:
                result["reasons"].append(f"Falta la imagen runtime fijada para {target}: {reference}.")
            else:
                result["runtimes"][target] = self._manifest["images"][target]["version"]

        if (
            result["engine_ready"]
            and result["isolation_boundary"]
            and result["seccomp"]
            and all(result["images"].values())
        ):
            result["available"] = True
        return result

    def verify_controls(self) -> dict[str, Any]:
        """Run trusted runtime self-checks and verify kernel controls inside each image."""
        status = self.status()
        if not status["available"]:
            return {"available": False, "status": status, "checks": {}}
        checks: dict[str, dict[str, Any]] = {}
        for target, reference in self._images.items():
            args = self._base_args(reference, "probe-" + uuid.uuid4().hex[:12], None)
            if target == "python":
                args.extend(
                    [
                        "python",
                        "-I",
                        "-c",
                        "import os,sys; print(sys.version.split()[0]); print(open('/proc/self/status').read())",
                    ]
                )
            else:
                args.extend(
                    [
                        "node",
                        "-e",
                        "console.log(process.version); console.log(require('node:fs').readFileSync('/proc/self/status','utf8'))",
                    ]
                )
            try:
                check = subprocess.run(args, capture_output=True, text=True, timeout=5, check=False)
            except (subprocess.TimeoutExpired, OSError) as error:
                checks[target] = {"passed": False, "reason": str(error)}
                continue
            text = check.stdout
            expected_uid = "10001\t10001\t10001\t10001"
            passed = (
                check.returncode == 0
                and "Seccomp:\t2" in text
                and "NoNewPrivs:\t1" in text
                and "CapEff:\t0000000000000000" in text
                and f"Uid:\t{expected_uid}" in text
            )
            checks[target] = {
                "passed": passed,
                "runtime_version": text.splitlines()[0] if text else None,
                "non_root_uid": "Uid:\t" + expected_uid in text,
                "no_new_privileges": "NoNewPrivs:\t1" in text,
                "seccomp_filter": "Seccomp:\t2" in text,
                "zero_capabilities": "CapEff:\t0000000000000000" in text,
                "exit_code": check.returncode,
                "stderr": check.stderr[-2048:],
            }
        return {"available": all(item["passed"] for item in checks.values()), "status": status, "checks": checks}

    def run_batch(
        self,
        target: str,
        code: str,
        inputs: list[str],
        source_hash: str,
        artifact_hash: str,
        run_id: str | None = None,
    ) -> RunResult:
        if target not in self._images:
            raise ValueError("Destino de runtime inválido.")
        for value in inputs:
            if "\n" in value or "\r" in value:
                raise ValueError("Cada entrada debe ocupar una sola línea.")
        readiness = self.status()
        if not readiness["available"]:
            raise RunnerUnavailable("RUN_SANDBOX_UNAVAILABLE", readiness)
        if not self._run_slots.acquire(blocking=False):
            raise RunnerBusy("RUN_CONCURRENCY_LIMIT")
        try:
            return self._run(target, code, inputs, source_hash, artifact_hash, interactive=False, run_id=run_id)
        finally:
            self._run_slots.release()

    async def start_interactive(
        self,
        target: str,
        code: str,
        source_hash: str,
        artifact_hash: str,
        run_id: str | None = None,
    ) -> InteractiveSession:
        if target not in self._images:
            raise ValueError("Destino de runtime inválido.")
        readiness = await asyncio.to_thread(self.status)
        if not readiness["available"]:
            raise RunnerUnavailable("RUN_SANDBOX_UNAVAILABLE", readiness)
        run_id = run_id or uuid.uuid4().hex
        if not all(char.isalnum() or char in "-_" for char in run_id):
            raise ValueError("run_id contiene caracteres no permitidos.")
        if not self._run_slots.acquire(blocking=False):
            raise RunnerBusy("RUN_CONCURRENCY_LIMIT")
        container_name = f"pseudo-studio-{run_id[:16]}"
        temp_directory = tempfile.TemporaryDirectory(prefix="pseudo-studio-run-")
        workdir = Path(temp_directory.name)
        workdir.chmod(0o711)
        extension = ".py" if target == "python" else ".js"
        program = workdir / ("main" + extension)
        program.write_text(code, encoding="utf-8", newline="\n")
        program.chmod(0o444)
        command = self._base_args(self._images[target], container_name, workdir)
        env_index = command.index("--workdir=/work")
        command[env_index:env_index] = ["--env", "PSEUDO_INTERACTIVE=1"]
        command.extend(["python", "-I", "/work/main.py"] if target == "python" else ["node", "/work/main.js"])
        with self._active_lock:
            if run_id in self._active:
                temp_directory.cleanup()
                self._run_slots.release()
                raise ValueError("run_id ya está activo.")
            self._active[run_id] = container_name
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except OSError as error:
            with self._active_lock:
                self._active.pop(run_id, None)
            temp_directory.cleanup()
            self._run_slots.release()
            raise RunnerUnavailable(f"No se pudo iniciar Docker: {error}") from error
        session = InteractiveSession(
            run_id,
            container_name,
            target,
            process,
            temp_directory,
            time.monotonic(),
            source_hash,
            artifact_hash,
            bytearray(),
            bytearray(),
        )
        with self._active_lock:
            cancelled_before_launch = run_id in self._cancelled
        if cancelled_before_launch:
            await asyncio.to_thread(self._kill, container_name)
        return session

    async def send_interactive_input(self, session: InteractiveSession, value: str) -> None:
        if "\n" in value or "\r" in value:
            raise ValueError("Cada respuesta debe ocupar una sola línea.")
        if session.process.stdin is None or session.process.returncode is not None:
            raise RuntimeError("La sesión ya no acepta entrada.")
        session.process.stdin.write(value.encode("utf-8") + b"\n")
        await session.process.stdin.drain()

    async def finish_interactive(self, session: InteractiveSession, *, cancelled: bool = False) -> RunResult:
        exit_code = await session.process.wait()
        with self._active_lock:
            self._active.pop(session.run_id, None)
            was_cancelled = cancelled or session.run_id in self._cancelled
            self._cancelled.discard(session.run_id)
        session.temp_directory.cleanup()
        if session.slot_held:
            session.slot_held = False
            self._run_slots.release()
        status = "completed"
        error_code = None
        if session.forced_status:
            status, error_code = session.forced_status
        elif was_cancelled:
            status, error_code = "cancelled", "RUN_CANCELLED"
        elif exit_code == 70:
            status, error_code = "runtime_error", self._runtime_error_code(session.stderr) or "RUN_RUNTIME_ERROR"
        elif exit_code == 71:
            status, error_code = "runtime_error", "RUN_INTERNAL"
        elif exit_code == 137:
            status, error_code = "runtime_error", "RUN_MEMORY"
        elif exit_code != 0:
            status, error_code = "runtime_error", "RUN_RUNTIME_ERROR"
        return RunResult(
            session.run_id,
            session.target,
            status,
            session.stdout.decode("utf-8", errors="replace"),
            session.stderr.decode("utf-8", errors="replace"),
            exit_code,
            (time.monotonic() - session.started) * 1000,
            error_code,
            session.source_hash,
            session.artifact_hash,
            self._manifest["images"][session.target]["version"],
        )

    def _run(
        self,
        target: str,
        code: str,
        inputs: list[str],
        source_hash: str,
        artifact_hash: str,
        *,
        interactive: bool,
        run_id: str | None = None,
    ) -> RunResult:
        run_id = run_id or uuid.uuid4().hex
        if not all(char.isalnum() or char in "-_" for char in run_id):
            raise ValueError("run_id contiene caracteres no permitidos.")
        container_name = f"pseudo-studio-{run_id[:16]}"
        extension = ".py" if target == "python" else ".js"
        runtime = "python" if target == "python" else "node"
        with tempfile.TemporaryDirectory(prefix="pseudo-studio-run-") as directory:
            workdir = Path(directory)
            workdir.chmod(0o711)
            program = workdir / ("main" + extension)
            program.write_text(code, encoding="utf-8", newline="\n")
            program.chmod(0o444)
            command = self._base_args(self._images[target], container_name, workdir)
            command.extend([runtime, "-I", "/work/main.py"] if target == "python" else [runtime, "/work/main.js"])
            if interactive:
                command[command.index("--read-only")] = "--read-only"
                env_index = command.index("--workdir=/work")
                command[env_index:env_index] = ["--env", "PSEUDO_INTERACTIVE=1"]
            input_bytes = ("\n".join(inputs) + ("\n" if inputs else "")).encode("utf-8")
            started = time.monotonic()
            with self._active_lock:
                if run_id in self._active:
                    raise ValueError("run_id ya está activo.")
                self._active[run_id] = container_name
            try:
                process = subprocess.Popen(
                    command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0
                )
            except OSError as error:
                with self._active_lock:
                    self._active.pop(run_id, None)
                raise RunnerUnavailable(f"No se pudo iniciar Docker: {error}") from error
            with self._active_lock:
                cancelled_before_launch = run_id in self._cancelled
            if cancelled_before_launch:
                self._kill(container_name)
            stdout, stderr, outcome = self._capture(process, container_name, input_bytes, started)
            with self._active_lock:
                self._active.pop(run_id, None)
                was_cancelled = run_id in self._cancelled
                self._cancelled.discard(run_id)
            if was_cancelled:
                outcome = ("cancelled", "RUN_CANCELLED")
        duration = (time.monotonic() - started) * 1000
        error_code = None
        status = "completed"
        if outcome:
            status, error_code = outcome
        elif process.returncode == 70:
            status = "runtime_error"
            error_code = self._runtime_error_code(stderr) or "RUN_RUNTIME_ERROR"
        elif process.returncode == 71:
            status = "runtime_error"
            error_code = "RUN_INTERNAL"
        elif process.returncode == 137:
            status = "runtime_error"
            error_code = "RUN_MEMORY"
        elif process.returncode not in (0, None):
            status = "runtime_error"
            error_code = "RUN_RUNTIME_ERROR"
        version = self._manifest["images"][target]["version"]
        return RunResult(
            run_id,
            target,
            status,
            stdout.decode("utf-8", errors="replace"),
            stderr.decode("utf-8", errors="replace"),
            process.returncode,
            duration,
            error_code,
            source_hash,
            artifact_hash,
            version,
        )

    def _base_args(self, image: str, container_name: str, workdir: Path | None) -> list[str]:
        args = [
            self._engine,
            "run",
            "--rm",
            "--interactive",
            "--name",
            container_name,
            "--network=none",
            "--read-only",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges",
            f"--security-opt=seccomp={self._seccomp}",
            f"--pids-limit={self.pids_limit}",
            f"--memory={self.memory_mb}m",
            f"--memory-swap={self.memory_mb}m",
            f"--cpus={self.cpu_limit}",
            "--ulimit=fsize=1048576:1048576",
            "--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=16m",
            "--user=10001:10001",
            "--workdir=/work" if workdir else "--workdir=/tmp",
        ]
        if workdir is not None:
            args.append(f"--mount=type=bind,src={workdir},dst=/work,readonly")
        args.append(image)
        return args

    def _capture(
        self,
        process: subprocess.Popen[bytes],
        container_name: str,
        input_bytes: bytes,
        started: float,
    ) -> tuple[bytearray, bytearray, tuple[str, str] | None]:
        assert process.stdin is not None and process.stdout is not None and process.stderr is not None
        selector = selectors.DefaultSelector()
        stdout, stderr = bytearray(), bytearray()
        stdin_fd = process.stdin.fileno()
        output_fds = {process.stdout.fileno(): stdout, process.stderr.fileno(): stderr}
        for stream in (process.stdout, process.stderr):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, "read")
        input_offset = 0
        outcome: tuple[str, str] | None = None
        if input_bytes:
            os.set_blocking(stdin_fd, False)
            selector.register(process.stdin, selectors.EVENT_WRITE, "write")
        else:
            process.stdin.close()
        while selector.get_map() or process.poll() is None:
            if time.monotonic() - started > self.timeout_seconds:
                outcome = ("timed_out", "RUN_TIMEOUT")
                self._kill(container_name)
                break
            for key, _ in selector.select(0.05):
                if key.data == "write":
                    try:
                        input_offset += os.write(stdin_fd, input_bytes[input_offset : input_offset + 8192])
                    except (BrokenPipeError, OSError):
                        input_offset = len(input_bytes)
                    if input_offset >= len(input_bytes):
                        selector.unregister(process.stdin)
                        process.stdin.close()
                else:
                    stream = key.fileobj
                    descriptor = stream.fileno()
                    try:
                        chunk = os.read(descriptor, 8192)
                    except BlockingIOError:
                        continue
                    if not chunk:
                        selector.unregister(stream)
                        stream.close()
                        continue
                    destination = output_fds[descriptor]
                    remaining = self.output_limit - len(stdout) - len(stderr)
                    if len(chunk) > remaining:
                        destination.extend(chunk[: max(0, remaining)])
                        outcome = ("output_limited", "RUN_OUTPUT_LIMIT")
                        self._kill(container_name)
                        break
                    destination.extend(chunk)
            if outcome:
                break
            if process.poll() is not None and not selector.get_map():
                break
        if process.poll() is None:
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
        else:
            process.wait()
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream and not stream.closed:
                stream.close()
        selector.close()
        return stdout, stderr, outcome

    def _kill(self, container_name: str) -> bool:
        try:
            result = subprocess.run([self._engine, "kill", container_name], capture_output=True, timeout=3, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return False
        return result.returncode == 0

    @staticmethod
    def _runtime_error_code(stderr: bytearray) -> str | None:
        prefix = b"PSEUDO_RUNTIME_ERROR "
        for line in bytes(stderr).splitlines():
            if line.startswith(prefix):
                try:
                    return str(json.loads(line[len(prefix) :]).get("code"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return None
        return None

    def cancel(self, run_id: str) -> bool:
        with self._active_lock:
            name = self._active.get(run_id)
        if not name:
            return False
        with self._active_lock:
            self._cancelled.add(run_id)
        deadline = time.monotonic() + 3
        while True:
            if self._kill(name):
                return True
            with self._active_lock:
                if run_id not in self._active:
                    return True
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.05)
