"""Text export formats shared by the API and local delivery tools."""

from __future__ import annotations

from typing import Any


def diagnostics_text(result: Any) -> str:
    lines = [
        "Pseudo / Studio · Reporte de análisis",
        f"SHA-256 de la fuente: {result.source_hash}",
        f"Versión del compilador: {result.compiler_version}",
        f"Estado: {'válida' if result.translatable else 'con errores'}",
        f"Diagnósticos: {len(result.diagnostics)}",
    ]
    for index, item in enumerate(result.diagnostics, start=1):
        lines.extend(
            [
                "",
                f"{index}. [{item.severity.upper()}] {item.code} · {item.stage}",
                f"   Ubicación: línea {item.span.start_line}, columna {item.span.start_column}",
                f"   {item.message}",
            ]
        )
        if item.hint:
            lines.append(f"   Sugerencia: {item.hint}")
    if not result.diagnostics:
        lines.extend(["", "Sin errores de compilación."])
    return "\n".join(lines) + "\n"
