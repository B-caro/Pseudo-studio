from __future__ import annotations

import json
import logging
import socket
import threading
import time

import pytest
import uvicorn
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from websockets.sync.client import connect

from backend.app import main
from backend.app.main import ExportRegistry, create_app
from backend.compiler.service import compile_source
from backend.projects.store import ProjectStore
from backend.runtime.runner import OciRunner


@pytest.fixture(scope="module")
def client(tmp_path_factory: pytest.TempPathFactory):
    data_dir = tmp_path_factory.mktemp("pseudo-api")
    main.DATA_DIR = data_dir
    store = ProjectStore(data_dir / "projects.sqlite3")
    app = create_app(store=store, runner=OciRunner(timeout_seconds=5))
    with TestClient(app) as test_client:
        yield test_client


def test_health_analyze_translate_and_invalid_diagnostics(client: TestClient) -> None:
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ready"

    source = 'Inicio\nLeer n\nEscribir "N=", n + 1\nFin\n'
    analyzed = client.post("/api/v1/analyze", json={"source": source})
    assert analyzed.status_code == 200
    assert analyzed.json()["translatable"] is True
    assert analyzed.json()["tokens"]
    assert analyzed.json()["ast"]

    translated = client.post("/api/v1/translate", json={"source": source})
    assert translated.status_code == 200
    assert set(translated.json()["artifacts"]) == {"python", "javascript"}
    assert translated.json()["source_hash"]
    assert "__ps_read_number" in translated.json()["artifacts"]["python"]["source"]
    assert "__ps_read_number" in translated.json()["artifacts"]["javascript"]["source"]

    invalid = client.post("/api/v1/translate", json={"source": "Inicio\nx = ?\nFin\n"})
    assert invalid.status_code == 422
    assert invalid.json()["detail"]["diagnostics"]
    grammar = client.get("/api/v1/grammar")
    assert grammar.status_code == 200
    assert grammar.headers["content-type"].startswith("text/plain")
    assert "programa" in grammar.text


def test_health_and_grammar_degraded_responses(client: TestClient, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(client.app.state.store, "health", lambda: False)
    degraded = client.get("/api/v1/health")
    assert degraded.status_code == 200
    assert degraded.json()["status"] == "degraded"
    assert degraded.json()["components"]["database"]["available"] is False

    monkeypatch.setattr(main, "ROOT", tmp_path)
    unavailable = client.get("/api/v1/grammar")
    assert unavailable.status_code == 503
    assert unavailable.json()["detail"]["code"] == "GRAMMAR_UNAVAILABLE"


@pytest.mark.parametrize("target", ["python", "javascript"])
def test_run_executes_compiled_program_inside_oci_and_records_history(client: TestClient, target: str) -> None:
    project_response = client.post("/api/v1/projects", json={"name": "API run", "source": "Inicio\nFin\n"})
    assert project_response.status_code == 201
    project = project_response.json()
    response = client.post(
        "/api/v1/run",
        json={
            "source": 'Inicio\nLeer n\nEscribir "Resultado: ", n + 1\nFin\n',
            "target": target,
            "inputs": {"values": ["41"]},
            "project_id": project["id"],
        },
    )
    assert response.status_code == 200, response.text
    run = response.json()
    assert (run["status"], run["exit_code"], run["stdout"], run["stderr"]) == (
        "completed",
        0,
        "Resultado: 42\n",
        "",
    )
    history = client.get(f"/api/v1/projects/{project['id']}/runs")
    assert history.status_code == 200
    assert len(history.json()["runs"]) == 1
    assert "inputs" not in history.json()["runs"][0]


def test_project_crud_optimistic_conflict_and_delete(client: TestClient) -> None:
    created = client.post("/api/v1/projects", json={"name": "Persistente", "source": "Inicio\nFin\n"})
    assert created.status_code == 201
    project = created.json()
    updated = client.put(
        f"/api/v1/projects/{project['id']}",
        json={
            "name": "Actualizado",
            "source": "Inicio\nEscribir 1\nFin\n",
            "version": 1,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["version"] == 2
    conflict = client.put(
        f"/api/v1/projects/{project['id']}",
        json={
            "name": "Obsoleto",
            "source": "Inicio\nFin\n",
            "version": 1,
        },
    )
    assert conflict.status_code == 409
    duplicate = client.post(f"/api/v1/projects/{project['id']}/duplicate")
    assert duplicate.status_code == 201
    assert duplicate.json()["source"] == updated.json()["source"]
    deleted = client.delete(f"/api/v1/projects/{project['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/projects/{project['id']}").status_code == 404


def test_catalog_projects_and_test_routes_positive_and_negative(client: TestClient, monkeypatch) -> None:
    catalog = client.get("/api/v1/examples")
    assert catalog.status_code == 200
    examples = catalog.json()["examples"]
    assert [item["id"] for item in examples] == list("ABCDE")
    assert all(item["case_count"] == 3 for item in examples)

    for example_id in "ABCDE":
        example = client.get(f"/api/v1/examples/{example_id}")
        assert example.status_code == 200
        assert example.json()["id"] == example_id
        assert example.json()["source"].startswith("Inicio")
        assert len(example.json()["cases"]) == 3
    assert client.get("/api/v1/examples/Z").status_code == 404

    created = client.post("/api/v1/projects", json={"name": "Route matrix", "source": "Inicio\nFin\n"})
    project_id = created.json()["id"]
    assert client.post("/api/v1/projects", json={"name": "", "source": "Inicio\nFin\n"}).status_code == 422
    assert any(item["id"] == project_id for item in client.get("/api/v1/projects").json()["projects"])
    assert client.get(f"/api/v1/projects/{project_id}").json()["name"] == "Route matrix"
    assert client.get(f"/api/v1/projects/{project_id}/runs").json() == {"runs": []}
    assert client.get("/api/v1/projects/missing-project/runs").status_code == 404
    assert (
        client.put(
            "/api/v1/projects/missing-project",
            json={"name": "missing", "source": "Inicio\nFin\n", "version": 1},
        ).status_code
        == 404
    )
    assert client.post("/api/v1/projects/missing-project/duplicate").status_code == 404
    assert client.delete("/api/v1/projects/missing-project").status_code == 404

    invalid_tests = client.post(
        "/api/v1/tests/run",
        json={
            "source": "Inicio\nEscribir @\nFin\n",
            "test_cases": [{"id": "bad", "inputs": [], "expected_stdout": ""}],
        },
    )
    assert invalid_tests.status_code == 422
    assert invalid_tests.json()["detail"]["code"] == "COMPILE_INVALID"

    original_verification = client.app.state.sandbox_verification
    client.app.state.sandbox_verification = {"available": False, "reason": "test-unavailable"}
    try:
        unavailable_tests = client.post(
            "/api/v1/tests/run",
            json={
                "source": "Inicio\nFin\n",
                "test_cases": [{"id": "one", "inputs": [], "expected_stdout": ""}],
            },
        )
        assert unavailable_tests.status_code == 503
        assert unavailable_tests.json()["detail"]["code"] == "RUN_SANDBOX_UNAVAILABLE"
    finally:
        client.app.state.sandbox_verification = original_verification

    missing_report = client.post("/api/v1/exports", json={"kind": "report-json", "report_id": "missing"})
    assert missing_report.status_code == 404
    assert missing_report.json()["detail"]["code"] == "TEST_REPORT_NOT_FOUND"
    assert client.post("/api/v1/exports", json={"kind": "unknown", "source": "Inicio\nFin\n"}).status_code == 422

    no_active_run = client.post("/api/v1/runs/not-active/cancel")
    assert no_active_run.status_code == 404
    assert no_active_run.json()["detail"]["code"] == "RUN_NOT_ACTIVE"
    cancellations: list[str] = []

    def cancel_active(run_id: str) -> bool:
        cancellations.append(run_id)
        return True

    monkeypatch.setattr(client.app.state.runner, "cancel", cancel_active)
    cancelled = client.post("/api/v1/runs/active-run_1/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json() == {"run_id": "active-run_1", "status": "cancellation_requested"}
    assert cancellations == ["active-run_1"]


def test_official_test_runner_and_real_downloadable_exports(client: TestClient) -> None:
    result = client.post(
        "/api/v1/tests/run",
        json={
            "source": 'Inicio\nLeer n\nEscribir "Suma: ", n + 1\nFin\n',
            "test_cases": [{"id": "one", "inputs": ["41"], "expected_stdout": "Suma: 42\n"}],
        },
    )
    assert result.status_code == 200, result.text
    report = result.json()
    assert (report["total"], report["passed"], report["failed"]) == (2, 2, 0)
    assert report["comparisons"] == [
        {
            "case_id": "one",
            "raw_stdout_match": True,
            "normalized_stdout_match": True,
            "raw_stderr_match": True,
            "normalized_stderr_match": True,
            "execution_match": True,
            "equivalent": True,
            "stdout_diff": "",
            "stderr_diff": "",
        }
    ]
    for kind, signature in (("report-json", b"{"), ("report-markdown", b"# Informe"), ("report-pdf", b"%PDF")):
        exported = client.post("/api/v1/exports", json={"kind": kind, "report_id": report["report_id"]})
        assert exported.status_code == 201
        downloaded = client.get(exported.json()["url"])
        assert downloaded.status_code == 200
        assert downloaded.content.startswith(signature)
        if kind == "report-json":
            assert json.loads(downloaded.content)["passed"] == 2
        assert "attachment; filename=" in downloaded.headers["content-disposition"]

    source_export = client.post("/api/v1/exports", json={"kind": "python", "source": "Inicio\nEscribir 3\nFin\n"})
    assert source_export.status_code == 201
    assert b"import sys as __ps_sys" in client.get(source_export.json()["url"]).content
    assert client.get("/api/v1/exports/not-a-valid-id").status_code == 404


def test_inspector_exports_match_selected_data_even_when_source_has_errors(client: TestClient) -> None:
    valid_source = "Inicio\nLeer numero\nEscribir numero + 1\nFin\n"
    for kind, expected_key in (("tokens", None), ("phases", None), ("ast", "kind"), ("symbols", None)):
        created = client.post("/api/v1/exports", json={"kind": kind, "source": valid_source})
        assert created.status_code == 201, created.text
        payload = json.loads(client.get(created.json()["url"]).content)
        if expected_key:
            assert payload[expected_key] == "Program"
        elif kind == "tokens":
            assert any(item["lexeme"] == "numero" for item in payload)
        elif kind == "phases":
            assert payload["lexical"]["status"] == "ok"
        else:
            assert any(item["name"] == "numero" for item in payload)

    invalid_source = "Inicio\nEscribir @\nFin\n"
    exported = client.post("/api/v1/exports", json={"kind": "diagnostics", "source": invalid_source})
    assert exported.status_code == 201, exported.text
    diagnostics = json.loads(client.get(exported.json()["url"]).content)
    assert any(item["code"] == "LEX_INVALID_CHAR" for item in diagnostics)
    assert client.post("/api/v1/exports", json={"kind": "ast", "source": invalid_source}).status_code == 422


@pytest.mark.parametrize(("target", "expected"), [("python", "N=42\n"), ("javascript", "N=42\n")])
def test_downloaded_generated_artifact_executes_inside_the_isolated_runtime(
    client: TestClient, target: str, expected: str
) -> None:
    source = 'Inicio\nLeer n\nEscribir "N=", n + 1\nFin\n'
    compiled = compile_source(source)
    artifact = compiled.artifacts[target]
    created = client.post("/api/v1/exports", json={"kind": target, "source": source})
    assert created.status_code == 201
    downloaded = client.get(created.json()["url"])
    assert downloaded.status_code == 200
    downloaded_source = downloaded.content.decode("utf-8")
    assert downloaded_source == artifact.source
    execution = client.app.state.runner.run_batch(
        target,
        downloaded_source,
        ["41"],
        compiled.source_hash,
        artifact.artifact_hash,
    )
    assert (execution.status, execution.exit_code, execution.stdout, execution.stderr) == (
        "completed",
        0,
        expected,
        "",
    )


def test_export_registry_rejects_path_traversal_ids(tmp_path) -> None:
    registry = ExportRegistry(tmp_path)
    assert registry.get("../projects") is None


def test_export_registry_recovers_downloads_after_api_restart(tmp_path) -> None:
    created = ExportRegistry(tmp_path).create("tokens", b'[{"lexeme":"inicio"}]')
    restored = ExportRegistry(tmp_path).get(created["id"])
    assert restored is not None
    path, filename, mime = restored
    assert path.read_bytes() == b'[{"lexeme":"inicio"}]'
    assert filename == created["filename"]
    assert mime == created["mime_type"]


@pytest.mark.parametrize("target", ["python", "javascript"])
def test_interactive_websocket_requests_real_input_and_streams_output(client: TestClient, target: str) -> None:
    source = 'Inicio\nEscribir "Numero?"\nLeer n\nEscribir "R=", n + 1\nFin\n'
    with client.websocket_connect("/api/v1/run/interactive") as websocket:
        websocket.send_json({"type": "start", "source": source, "target": target})
        events = []
        while True:
            event = websocket.receive_json()
            events.append(event)
            if event["event"] == "input_requested":
                websocket.send_json({"type": "input", "value": "41"})
            if event["event"] in {"exited", "error"}:
                break
    assert events[0]["event"] == "started"
    assert any(event["event"] == "input_requested" for event in events)
    assert "Numero?\n" in "".join(event.get("data", "") for event in events if event["event"] == "stdout")
    exited = events[-1]
    assert (exited["status"], exited["exit_code"], exited["stdout"]) == ("completed", 0, "Numero?\nR=42\n")


def test_websocket_disconnect_kills_container_and_releases_session(tmp_path) -> None:
    source = "Inicio\ni = 0\nMientras Verdadero Hacer\ni = i + 1\nFinMientras\nFin\n"
    runner = OciRunner(timeout_seconds=10)
    app = create_app(store=ProjectStore(tmp_path / "disconnect.sqlite3"), runner=runner)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    run_id = None
    try:
        deadline = time.monotonic() + 10
        while not server.started and server_thread.is_alive() and time.monotonic() < deadline:
            time.sleep(0.02)
        assert server.started, "Uvicorn no inició para la prueba real de desconexión."
        with connect(
            f"ws://127.0.0.1:{port}/api/v1/run/interactive",
            origin="http://127.0.0.1:5173",
            open_timeout=5,
            close_timeout=1,
        ) as websocket:
            websocket.send(json.dumps({"type": "start", "source": source, "target": "python"}))
            started = json.loads(websocket.recv(timeout=10))
            assert started["event"] == "started"
            run_id = started["run_id"]

        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            with runner._active_lock:
                active = run_id in runner._active
            if not active:
                break
            time.sleep(0.05)
        assert not active, "La desconexión dejó un contenedor interactivo activo."
    finally:
        if run_id is not None:
            with runner._active_lock:
                still_active = run_id in runner._active
            if still_active:
                runner.cancel(run_id)
        server.should_exit = True
        server_thread.join(timeout=5)


def test_interactive_idle_input_expires_and_returns_timeout(client: TestClient) -> None:
    runner = client.app.state.runner
    original_timeout = runner.timeout_seconds
    runner.timeout_seconds = 2.5
    try:
        with client.websocket_connect("/api/v1/run/interactive") as websocket:
            websocket.send_json({"type": "start", "source": "Inicio\nLeer n\nFin\n", "target": "javascript"})
            events = []
            while True:
                event = websocket.receive_json()
                events.append(event)
                if event["event"] in {"exited", "error"}:
                    break
        assert any(event["event"] == "input_requested" for event in events)
        assert events[-1]["event"] == "exited"
        assert (events[-1]["status"], events[-1]["error_code"]) == ("timed_out", "RUN_TIMEOUT")
    finally:
        runner.timeout_seconds = original_timeout


def test_api_rejects_unknown_fields_invalid_targets_and_oversized_content_length(client: TestClient) -> None:
    unknown = client.post("/api/v1/analyze", json={"source": "Inicio\nFin\n", "pretend": True})
    assert unknown.status_code == 422
    target = client.post("/api/v1/run", json={"source": "Inicio\nFin\n", "target": "shell"})
    assert target.status_code == 422
    too_large = client.post(
        "/api/v1/analyze",
        content=json.dumps({"source": "x"}),
        headers={"content-type": "application/json", "content-length": "1048577"},
    )
    assert too_large.status_code == 413


def test_api_error_status_matrix_is_structured_and_has_no_tracebacks(client: TestClient, monkeypatch) -> None:
    invalid_run_id = client.post("/api/v1/runs/bad%21id/cancel")
    assert invalid_run_id.status_code == 400

    missing_project = client.get("/api/v1/projects/missing-project")
    assert missing_project.status_code == 404
    assert missing_project.json()["detail"]["code"] == "PROJECT_NOT_FOUND"

    invalid_source = client.post("/api/v1/translate", json={"source": "Inicio\nx = ?\nFin\n"})
    assert invalid_source.status_code == 422
    assert "diagnostics" in invalid_source.json()["detail"]

    invalid_run_source = client.post(
        "/api/v1/run",
        json={"source": "Inicio\nEscribir @\nFin\n", "target": "python", "inputs": {"values": []}},
    )
    assert invalid_run_source.status_code == 422
    assert invalid_run_source.json()["detail"]["code"] == "COMPILE_INVALID"

    monkeypatch.setattr(main, "RATE_LIMIT_PER_MINUTE", 0)
    limited = client.post("/api/v1/analyze", json={"source": "Inicio\nFin\n"})
    assert limited.status_code == 429
    assert limited.headers["retry-after"] == "60"
    monkeypatch.undo()

    original_verification = client.app.state.sandbox_verification
    client.app.state.sandbox_verification = {"available": False, "reason": "test-unavailable"}
    unavailable = client.post(
        "/api/v1/run",
        json={"source": "Inicio\nFin\n", "target": "python", "inputs": {"values": []}},
    )
    client.app.state.sandbox_verification = original_verification
    assert unavailable.status_code == 503
    assert unavailable.json()["detail"]["code"] == "RUN_SANDBOX_UNAVAILABLE"
    assert "traceback" not in unavailable.text.lower()


def test_request_correlation_is_returned_without_logging_source_text(client: TestClient, caplog) -> None:
    private_text = "never-write-this-source-to-logs"
    with caplog.at_level(logging.INFO, logger="pseudo_studio.api"):
        response = client.post(
            "/api/v1/analyze",
            json={"source": f'Inicio\nEscribir "{private_text}"\nFin\n'},
            headers={"X-Request-ID": "trace-audit-42"},
        )
    assert response.status_code == 200
    assert response.headers["x-request-id"] == "trace-audit-42"
    assert private_text not in caplog.text


def test_interactive_websocket_rejects_untrusted_origin(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect) as disconnected:
        with client.websocket_connect("/api/v1/run/interactive", headers={"origin": "https://attacker.invalid"}):
            pytest.fail("La conexión WebSocket de un origen ajeno no fue rechazada.")
    assert disconnected.value.code == 4403


def test_interactive_websocket_protocol_compile_and_sandbox_failures(client: TestClient) -> None:
    with client.websocket_connect("/api/v1/run/interactive") as websocket:
        websocket.send_json({"type": "not-start"})
        assert websocket.receive_json()["code"] == "WS_PROTOCOL_ERROR"

    with client.websocket_connect("/api/v1/run/interactive") as websocket:
        websocket.send_json({"type": "start", "source": "Inicio\nEscribir @\nFin\n", "target": "python"})
        event = websocket.receive_json()
        assert event["code"] == "COMPILE_INVALID"
        assert event["diagnostics"]

    original_verification = client.app.state.sandbox_verification
    client.app.state.sandbox_verification = {"available": False, "reason": "test-unavailable"}
    try:
        with client.websocket_connect("/api/v1/run/interactive") as websocket:
            websocket.send_json({"type": "start", "source": "Inicio\nFin\n", "target": "python"})
            event = websocket.receive_json()
            assert event["code"] == "RUN_SANDBOX_UNAVAILABLE"
    finally:
        client.app.state.sandbox_verification = original_verification
