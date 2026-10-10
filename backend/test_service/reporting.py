from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

import reportlab
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas


def report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Informe de pruebas — Pseudo / Studio",
        "",
        f"- Fecha UTC: `{report['generated_at']}`",
        f"- Fuente SHA-256: `{report['source_hash']}`",
        f"- Compilador: `{report['compiler_version']}`",
        f"- Resultado: **{report['passed']}/{report['total']} casos destino**",
        "",
        "| Caso | Destino | Estado | Exit | Duración ms | Inputs | Expected stdout | Actual stdout | stderr | Hash artefacto |",
        "|---|---|---|---:|---:|---|---|---|---|---|",
    ]
    for item in report["runs"]:
        fields = [
            item["case_id"],
            item["target"],
            item["status"],
            str(item["exit_code"]),
            f"{item['duration_ms']:.2f}",
            json.dumps(item["inputs"], ensure_ascii=False),
            item["expected_stdout"],
            item["actual_stdout"],
            item["stderr"],
            item["artifact_hash"],
        ]
        lines.append("| " + " | ".join(value.replace("\n", "\\n").replace("|", "\\|") for value in fields) + " |")
    return "\n".join(lines) + "\n"


def report_pdf(report: dict[str, Any]) -> bytes:
    font_dir = Path(reportlab.__file__).parent / "fonts"
    regular = font_dir / "Vera.ttf"
    bold = font_dir / "VeraBd.ttf"
    if not regular.is_file() or not bold.is_file():
        raise RuntimeError("No están disponibles las fuentes Unicode requeridas para el informe PDF.")
    if "PseudoVera" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("PseudoVera", str(regular)))
        pdfmetrics.registerFont(TTFont("PseudoVera-Bold", str(bold)))
    buffer = io.BytesIO()
    canvas = Canvas(buffer, pagesize=A4, pageCompression=1)
    canvas.setTitle("Pseudo / Studio — Informe de pruebas")
    canvas.setAuthor("Pseudo / Studio")
    width, height = A4
    x, y = 42, height - 44

    def draw_text(text: str, *, bold_text: bool = False, gap: float = 13) -> None:
        nonlocal y
        font = "PseudoVera-Bold" if bold_text else "PseudoVera"
        wrapped = simpleSplit(text, font, 8.5, width - 84)
        canvas.setFont(font, 8.5)
        for line in wrapped or [""]:
            if y < 48:
                canvas.showPage()
                y = height - 44
                canvas.setFont(font, 8.5)
            canvas.drawString(x, y, line)
            y -= gap

    draw_text("Pseudo / Studio — Informe de pruebas", bold_text=True, gap=19)
    draw_text(f"Fecha UTC: {report['generated_at']}")
    draw_text(f"Fuente SHA-256: {report['source_hash']}")
    draw_text(f"Compilador: {report['compiler_version']}")
    draw_text(f"Resultado: {report['passed']}/{report['total']} ejecuciones destino aprobadas", bold_text=True, gap=18)
    for run in report["runs"]:
        draw_text(
            f"{run['case_id']} · {run['target']} · {run['status']} · exit {run['exit_code']} · {run['duration_ms']:.2f} ms",
            bold_text=True,
            gap=12,
        )
        draw_text("Inputs: " + json.dumps(run["inputs"], ensure_ascii=False))
        draw_text("Expected stdout: " + repr(run["expected_stdout"]))
        draw_text("Actual stdout: " + repr(run["actual_stdout"]))
        if run["stderr"]:
            draw_text("stderr: " + repr(run["stderr"]))
        draw_text("Source SHA-256: " + run["source_hash"])
        draw_text("Artifact SHA-256: " + run["artifact_hash"], gap=17)
    canvas.save()
    return buffer.getvalue()
