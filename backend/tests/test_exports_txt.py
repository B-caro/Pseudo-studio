from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app import main
from backend.app.main import create_app
from backend.projects.store import ProjectStore


class RuntimeUnavailable:
    def verify_controls(self) -> dict[str, object]:
        return {"available": False, "reason": "Test sin motor OCI"}

    def status(self) -> dict[str, object]:
        return {"available": False, "engine_ready": False}


def test_txt_exports_preserve_complete_generated_artifact(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(main, "DATA_DIR", tmp_path)
    app = create_app(store=ProjectStore(tmp_path / "projects.sqlite3"), runner=RuntimeUnavailable())
    source = 'Inicio\nLeer numero\nEscribir "Resultado: ", numero + 1\nFin\n'

    with TestClient(app) as client:
        for native_kind, text_kind in (("python", "python-txt"), ("javascript", "javascript-txt")):
            native = client.post("/api/v1/exports", json={"kind": native_kind, "source": source})
            text = client.post("/api/v1/exports", json={"kind": text_kind, "source": source})
            assert native.status_code == text.status_code == 201
            native_download = client.get(native.json()["url"])
            text_download = client.get(text.json()["url"])
            assert native_download.content == text_download.content
            assert text_download.headers["content-type"].startswith("text/plain")
            assert text_download.headers["content-disposition"].endswith('.txt"')


def test_diagnostics_txt_includes_hash_location_message_and_hint_for_invalid_source(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(main, "DATA_DIR", tmp_path)
    app = create_app(store=ProjectStore(tmp_path / "projects.sqlite3"), runner=RuntimeUnavailable())
    invalid_source = "Inicio\nEscribir @\nFin\n"

    with TestClient(app) as client:
        exported = client.post("/api/v1/exports", json={"kind": "diagnostics-txt", "source": invalid_source})
        assert exported.status_code == 201, exported.text
        downloaded = client.get(exported.json()["url"])
        text = downloaded.content.decode("utf-8")
        assert exported.json()["filename"].endswith(".txt")
        assert "SHA-256 de la fuente:" in text
        assert "Estado: con errores" in text
        assert "LEX_INVALID_CHAR" in text
        assert "Ubicación: línea 2, columna 10" in text
        assert "Sugerencia:" in text

        invalid_code = client.post("/api/v1/exports", json={"kind": "python-txt", "source": invalid_source})
        assert invalid_code.status_code == 422


def test_diagnostics_txt_reports_success_for_valid_source(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(main, "DATA_DIR", tmp_path)
    app = create_app(store=ProjectStore(tmp_path / "projects.sqlite3"), runner=RuntimeUnavailable())

    with TestClient(app) as client:
        exported = client.post(
            "/api/v1/exports", json={"kind": "diagnostics-txt", "source": "Inicio\nEscribir 1\nFin\n"}
        )
        assert exported.status_code == 201
        text = client.get(exported.json()["url"]).text
        assert "Estado: válida" in text
        assert "Sin errores de compilación." in text
