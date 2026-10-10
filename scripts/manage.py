#!/usr/bin/env python3
"""Portable local bootstrap, lifecycle, health and integration smoke commands."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
DATA = ROOT / "data"
RUN_DIR = DATA / "run"
LOG_DIR = DATA / "logs"
API_URL = os.environ.get("PSEUDO_STUDIO_API_URL", "http://127.0.0.1:8000")
WEB_URL = os.environ.get("PSEUDO_STUDIO_WEB_URL", "http://127.0.0.1:5173")
PYPI_INDEX = os.environ.get("PSEUDO_PYPI_INDEX", "https://pypi.org/simple")


def venv_python() -> Path:
    return ROOT / (".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python")


def require_python_version() -> None:
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError(f"Python 3.12 es obligatorio; se ejecuta {sys.version.split()[0]}.")


def load_local_env() -> dict[str, str]:
    values = os.environ.copy()
    env_file = ROOT / ".env"
    if not env_file.exists():
        return values
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if key and key.replace("_", "").isalnum():
            values.setdefault(key, value.strip("\"'"))
    return values


def invoke(command: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> None:
    print("$ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def bootstrap(_: argparse.Namespace) -> None:
    require_python_version()
    node = shutil.which("node")
    npm = shutil.which("npm")
    if not node or not npm:
        raise RuntimeError("Node.js 22+ y npm 10+ son necesarios. Instala Node.js antes de continuar.")
    node_version = subprocess.check_output([node, "--version"], text=True).strip()
    if int(node_version.removeprefix("v").split(".", 1)[0]) < 22:
        raise RuntimeError(f"Node.js 22+ es obligatorio; se encontró {node_version}.")
    python_env = venv_python()
    if not python_env.exists():
        invoke([sys.executable, "-m", "venv", str(ROOT / ".venv")])
    pip_env = os.environ.copy()
    pip_env["PIP_INDEX_URL"] = PYPI_INDEX
    invoke([str(python_env), "-m", "pip", "install", "--upgrade", "pip"], env=pip_env)
    lock = ROOT / "requirements.lock"
    if lock.exists():
        invoke([str(python_env), "-m", "pip", "install", "--index-url", PYPI_INDEX, "-r", str(lock)], env=pip_env)
        invoke([str(python_env), "-m", "pip", "install", "--no-deps", "-e", str(ROOT)], env=pip_env)
    else:
        invoke(
            [str(python_env), "-m", "pip", "install", "--index-url", PYPI_INDEX, "-e", ".[dev]"],
            env=pip_env,
        )
    npm_command = [npm, "ci"]
    if os.name == "nt" and npm.lower().endswith((".cmd", ".bat")):
        npm_command = [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/s", "/c", "npm ci"]
    invoke(npm_command, cwd=FRONTEND)
    invoke([node, str(FRONTEND / "node_modules/playwright/cli.js"), "install", "chromium"], cwd=FRONTEND)
    image_manifest = json.loads((ROOT / "sandbox/runtime-images.json").read_text(encoding="utf-8"))
    runtime_environment = load_local_env()
    engine = runtime_environment.get("PSEUDO_STUDIO_OCI_ENGINE", "docker")
    if not shutil.which(engine):
        raise RuntimeError(f"No se encontró el engine OCI '{engine}'. Instálalo antes de descargar los runtimes.")
    for image in image_manifest["images"].values():
        invoke([engine, "pull", image["reference"]], env=runtime_environment)
    print("Dependencias Python y JavaScript, Chromium e imágenes OCI por digest están instalados.")


def _http_json(url: str, *, method: str = "GET", body: Any = None, timeout: float = 8.0) -> tuple[int, Any]:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"content-type": "application/json"} if data is not None else {},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content = response.read()
            return response.status, json.loads(content) if content else None
    except urllib.error.HTTPError as error:
        data = error.read()
        try:
            detail = json.loads(data)
        except json.JSONDecodeError:
            detail = data.decode("utf-8", errors="replace")
        return error.code, detail


def _http_text(url: str, timeout: float = 3.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status == 200
    except (OSError, urllib.error.URLError):
        return False


def _runner_verification() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT))
    from backend.runtime.runner import OciRunner

    with patch.dict(os.environ, load_local_env()):
        return OciRunner().verify_controls()


def verify(_: argparse.Namespace) -> None:
    require_python_version()
    if not venv_python().exists():
        raise RuntimeError("Falta .venv; ejecuta `python3.12 scripts/manage.py bootstrap` primero.")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from backend.compiler.service import compile_source

    result = compile_source('Inicio\nLeer numero\nEscribir "OK=", numero + 1\nFin\n')
    if not result.translatable:
        raise RuntimeError(f"El compilador no aceptó el smoke source: {[d.to_dict() for d in result.diagnostics]}")
    print(f"Compilador {result.compiler_version}; source SHA-256 {result.source_hash}.")
    verification = _runner_verification()
    print(json.dumps(verification, ensure_ascii=False, indent=2))
    if not verification["available"]:
        raise RuntimeError("El sandbox no pasó las comprobaciones rootless/VM, seccomp, UID y capacidades.")


def _process_command(kind: str) -> list[str]:
    python_env = venv_python()
    if kind == "api":
        return [str(python_env), "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"]
    node = shutil.which("node")
    if not node:
        raise RuntimeError("No se encontró Node.js.")
    return [node, str(FRONTEND / "node_modules/vite/bin/vite.js"), "--host", "127.0.0.1", "--port", "5173"]


def _pid_file(kind: str) -> Path:
    return RUN_DIR / f"{kind}.json"


def _pid_is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def start(_: argparse.Namespace) -> None:
    require_python_version()
    if not venv_python().exists() or not (FRONTEND / "node_modules/vite/bin/vite.js").exists():
        raise RuntimeError("Dependencias incompletas; ejecuta `python3.12 scripts/manage.py bootstrap`.")
    verification = _runner_verification()
    if not verification["available"]:
        raise RuntimeError("Sandbox no disponible; revisa `python3.12 scripts/manage.py verify`.")
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    environment = load_local_env()
    launched: list[tuple[subprocess.Popen[bytes], Any, str]] = []
    try:
        for kind in ("api", "web"):
            file = _pid_file(kind)
            if file.exists():
                try:
                    previous = json.loads(file.read_text(encoding="utf-8"))
                    if _pid_is_running(int(previous["pid"])):
                        continue
                except (OSError, ValueError, KeyError, json.JSONDecodeError):
                    pass
                file.unlink(missing_ok=True)
            url = f"{API_URL}/api/v1/health" if kind == "api" else WEB_URL
            if _http_text(url):
                continue
            log_file = (LOG_DIR / f"{kind}.log").open("ab")
            process = subprocess.Popen(
                _process_command(kind),
                cwd=ROOT if kind == "api" else FRONTEND,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=os.name != "nt",
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
            )
            _pid_file(kind).write_text(json.dumps({"pid": process.pid, "kind": kind}), encoding="utf-8")
            launched.append((process, log_file, kind))
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if not all(_http_text(url) for url in (f"{API_URL}/api/v1/health", WEB_URL)):
                time.sleep(0.25)
                continue
            status, health = _http_json(f"{API_URL}/api/v1/health")
            if status == 200 and health.get("status") == "ready":
                print(f"API: {API_URL}/api/v1/docs")
                print(f"Studio: {WEB_URL}")
                print(f"Logs: {LOG_DIR}")
                return
            time.sleep(0.5)
        raise RuntimeError("Los servicios no quedaron listos en 30 segundos; revisa data/logs/api.log y web.log.")
    except Exception:
        for process, log_file, _ in launched:
            process.terminate()
            log_file.close()
        raise
    finally:
        for _, log_file, _ in launched:
            if not log_file.closed:
                log_file.close()


def stop(_: argparse.Namespace) -> None:
    for kind in ("web", "api"):
        file = _pid_file(kind)
        if not file.exists():
            print(f"{kind}: sin PID administrado por este script")
            continue
        try:
            entry = json.loads(file.read_text(encoding="utf-8"))
            pid = int(entry["pid"])
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            file.unlink(missing_ok=True)
            continue
        if not _pid_is_running(pid):
            file.unlink(missing_ok=True)
            print(f"{kind}: proceso ya detenido")
            continue
        try:
            os.kill(pid, signal.SIGTERM)
            deadline = time.monotonic() + 5
            while _pid_is_running(pid) and time.monotonic() < deadline:
                time.sleep(0.1)
            if _pid_is_running(pid):
                os.kill(pid, signal.SIGKILL)
        except OSError as error:
            print(f"{kind}: no se pudo detener PID {pid}: {error}", file=sys.stderr)
        file.unlink(missing_ok=True)
        print(f"{kind}: detenido")


def smoke(_: argparse.Namespace) -> None:
    status, health = _http_json(f"{API_URL}/api/v1/health")
    if status != 200 or health.get("status") != "ready":
        raise RuntimeError(f"API no lista: HTTP {status} {health}")
    if not _http_text(WEB_URL):
        raise RuntimeError(f"Frontend no responde en {WEB_URL}.")
    source = 'Inicio\nLeer n\nEscribir "OK=", n + 1\nFin\n'
    status, analysis = _http_json(f"{API_URL}/api/v1/analyze", method="POST", body={"source": source})
    if status != 200 or not analysis.get("translatable") or not analysis.get("tokens") or not analysis.get("ast"):
        raise RuntimeError(f"Análisis smoke falló: HTTP {status} {analysis}")
    status, translation = _http_json(
        f"{API_URL}/api/v1/translate",
        method="POST",
        body={"source": source, "targets": ["python", "javascript"]},
    )
    if status != 200 or set(translation.get("artifacts", {})) != {"python", "javascript"}:
        raise RuntimeError(f"Traducción smoke falló: HTTP {status} {translation}")
    for target in ("python", "javascript"):
        status, run = _http_json(
            f"{API_URL}/api/v1/run",
            method="POST",
            body={"source": source, "target": target, "inputs": {"values": ["41"]}},
            timeout=15,
        )
        if status != 200 or run.get("status") != "completed" or run.get("stdout") != "OK=42\n":
            raise RuntimeError(f"Ejecución smoke {target} falló: HTTP {status} {run}")
        print(f"{target}: {run['stdout'].strip()} · {run['runtime_version']} · {run['artifact_hash']}")
    print(f"Smoke completo; source SHA-256 {analysis['source_hash']}.")


def backup(args: argparse.Namespace) -> None:
    environment = load_local_env()
    database = Path(environment.get("PSEUDO_STUDIO_DB_PATH", str(DATA / "projects.sqlite3"))).expanduser()
    if not database.is_absolute():
        database = ROOT / database
    if not database.is_file():
        raise RuntimeError(f"No existe la base SQLite: {database}")
    if args.output:
        destination = Path(args.output).expanduser()
        if not destination.is_absolute():
            destination = ROOT / destination
    else:
        from datetime import datetime, timezone

        destination = DATA / "backups" / f"projects-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.sqlite3"
    if destination.resolve() == database.resolve():
        raise RuntimeError("El destino del backup debe ser distinto de la base activa.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database) as source, sqlite3.connect(destination) as target:
        source.backup(target)
        integrity = target.execute("PRAGMA quick_check").fetchone()
    if not integrity or integrity[0] != "ok":
        destination.unlink(missing_ok=True)
        raise RuntimeError(f"El backup no superó PRAGMA quick_check: {integrity}")
    print(f"Backup íntegro: {destination} ({destination.stat().st_size} bytes)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name, handler, help_text in (
        ("bootstrap", bootstrap, "Instala Python, npm y Chromium de Playwright."),
        ("start", start, "Verifica aislamiento y arranca API y frontend en loopback."),
        ("stop", stop, "Detiene los servicios iniciados por este script."),
        ("verify", verify, "Valida Python, compilador y controles del runtime OCI."),
        ("smoke", smoke, "Prueba salud, análisis, traducción y ambos runtimes por API."),
        ("backup", backup, "Copia la base SQLite con la API de backup y verifica integridad."),
    ):
        command = commands.add_parser(name, help=help_text)
        if name == "backup":
            command.add_argument("--output", help="Ruta destino; por defecto data/backups con timestamp.")
        command.set_defaults(handler=handler)
    args = parser.parse_args()
    try:
        args.handler(args)
    except (RuntimeError, subprocess.CalledProcessError, OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
