"""Build a traceable Phase 3 package from official sources and the real compiler."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "delivery" / "fase-3"
STAGING = ROOT / "delivery" / ".fase-3-build"
DOCUMENTS = (
    "INFORME_FASE_2.md",
    "INFORME_FASE_3.md",
    "GUION_DEFENSA_FASE_2.md",
    "GUION_DEFENSA_FASE_3.md",
    "AST_Y_RECorrido.md",
    "LANGUAGE_CONFORMANCE_MATRIX.md",
    "MATRIZ_BRECHAS_RUBRICAS.md",
    "REQUERIMIENTOS_FASES_2_3.md",
    "EXTENDED_TESTING.md",
    "TRACEABILITY.md",
    "VALIDATION_REPORT.md",
    "DECISIONS.md",
    "API_ROUTE_MATRIX.md",
)


def main() -> int:
    if STAGING.exists():
        shutil.rmtree(STAGING)

    sys.path.insert(0, str(ROOT))
    from backend.app.exports import diagnostics_text
    from backend.compiler.service import compile_source

    sources = STAGING / "fuentes"
    translations = STAGING / "traducciones"
    errors = STAGING / "errores"
    evidence = STAGING / "evidencia"
    documents = STAGING / "documentos"
    for directory in (sources, translations, errors, evidence, documents):
        directory.mkdir(parents=True, exist_ok=True)

    for name in "ABCDE":
        source_path = ROOT / "examples" / f"{name}.psc"
        source_text = source_path.read_text(encoding="utf-8")
        result = compile_source(source_text)
        if not result.translatable:
            raise SystemExit(f"No se pudo generar el programa oficial {name}: {result.diagnostics}")
        (sources / f"{name}.txt").write_text(source_text, encoding="utf-8", newline="")
        for target, extension in (("python", ".py"), ("javascript", ".js")):
            artifact = result.artifacts[target].source.encode("utf-8")
            (translations / f"{name}.{target}{extension}").write_bytes(artifact)
            (translations / f"{name}.{target}.txt").write_bytes(artifact)

    shutil.copyfile(ROOT / "examples" / "official-cases.json", evidence / "casos-oficiales.json")
    shutil.copytree(ROOT / "examples" / "extended", evidence / "casos-extendidos")
    reports = evidence / "reportes"
    reports.mkdir()
    for name in (
        "acceptance-results.json",
        "acceptance-results.md",
        "extended-acceptance-results.json",
        "extended-acceptance-results.md",
        "phase1-manual-acceptance.json",
        "phase1-manual-acceptance.md",
        "compiler-performance.json",
        "compiler-performance.md",
        "phase1-execution-python.png",
        "phase1-execution-javascript.png",
        "phase2-execution-c.png",
        "phase2-execution-d.png",
    ):
        shutil.copyfile(ROOT / "reports" / name, reports / name)
    bad_source = "Inicio\nEscribir @\nFin\n"
    (errors / "fuente-invalida.txt").write_text(bad_source, encoding="utf-8", newline="")
    invalid = compile_source(bad_source, targets=())
    (errors / "diagnosticos.txt").write_text(diagnostics_text(invalid), encoding="utf-8", newline="")
    for name in DOCUMENTS:
        shutil.copyfile(ROOT / "docs" / name, documents / name)

    official = json.loads((ROOT / "reports" / "acceptance-results.json").read_text(encoding="utf-8"))
    extended = json.loads((ROOT / "reports" / "extended-acceptance-results.json").read_text(encoding="utf-8"))
    (evidence / "ESTADO.md").write_text(
        f"""# Estado de evidencia de ejecución

Paquete generado desde el compilador actual. A–E conserva las fuentes oficiales; los 10 artefactos de Python y JavaScript se generan con `compile_source`. Los pares `.py/.js` y `.txt` son byte a byte idénticos. Este paquete incluye casos extendidos, reportes de runtime y capturas del navegador.

- A–E: **{official["passed"]}/{official["total"]}** ejecuciones OCI reales, fecha `{official["generated_at"]}`.
- Casos extendidos/negativos/runtime: **{extended["passed_checks"]}/{extended["total_checks"]}** checks, fecha `{extended["generated_at"]}`.
- Runtime: Docker Desktop VM (`docker-desktop-vm`), Python `{official["sandbox"]["status"]["runtimes"]["python"]}`, Node `{official["sandbox"]["status"]["runtimes"]["javascript"]}`; controles y cuotas en los JSON incluidos.
- Validación completa, limitaciones y hashes: `reportes/` y `docs/VALIDATION_REPORT.md` del repositorio.

La frontera Docker Desktop VM está verificada; no se presenta el daemon como rootless. La auditoría manual con lector de pantalla, pruebas nativas macOS/Linux rootless, CI remota dispensada por el usuario y render final del DOCX aún no están certificadas.
""",
        encoding="utf-8",
        newline="",
    )
    (STAGING / "README.md").write_text(
        """# Paquete académico de Fase 3

`fuentes/` contiene A–E como UTF-8 `.txt`; `traducciones/` contiene los artefactos completos generados por el compilador como extensión nativa y como `.txt`. Cada par de destino es byte a byte idéntico. `errores/` contiene una fuente inválida y el diagnóstico real; `evidencia/` incluye fixtures, casos extendidos, reportes y capturas; `documentos/` reúne informes, guiones y matrices.

Para regenerar artefactos desde el repositorio: `python3.12 scripts/build_phase3_package.py`. Para validar el aislamiento y repetir A–E: `python3.12 scripts/manage.py verify` y `python3.12 scripts/run_official_acceptance.py`. Las pruebas ampliadas se repiten con `python3.12 scripts/run_extended_acceptance.py`; suite completa: `.venv/bin/pytest -q`; E2E: `npm --prefix frontend run test:e2e`. La evidencia incluida es la corrida registrada en `evidencia/reportes/`.
""",
        encoding="utf-8",
        newline="",
    )

    files = sorted(path for path in STAGING.rglob("*") if path.is_file() and path.name != "SHA256SUMS")
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(STAGING).as_posix()}" for path in files
    ]
    (STAGING / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    STAGING.replace(OUTPUT)
    print(f"Paquete creado: {OUTPUT.relative_to(ROOT)} ({len(files)} archivos con hash)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
