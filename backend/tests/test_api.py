from __future__ import annotations

import json
import logging

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

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
