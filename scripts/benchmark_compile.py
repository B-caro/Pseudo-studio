#!/usr/bin/env python3
"""Measure lexer/parser/semantic analysis latency for 100- and 1,000-line inputs."""

from __future__ import annotations

import json
import os
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.compiler.service import compile_source  # noqa: E402


def make_source(line_count: int) -> str:
    if line_count < 3:
        raise ValueError("line_count debe contar al menos Inicio, una sentencia y Fin.")
    statements = [f"valor_{index} = {index}" for index in range(line_count - 2)]
    return "\n".join(["Inicio", *statements, "Fin", ""])


def measure(line_count: int, iterations: int) -> dict[str, object]:
    source = make_source(line_count)
    warmup = compile_source(source, targets=())
    if not warmup.translatable:
        raise RuntimeError(f"El caso de {line_count} líneas no compila: {warmup.diagnostics}")
    timings_ms = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = compile_source(source, targets=())
        timings_ms.append((time.perf_counter() - start) * 1000)
        if not result.translatable:
            raise RuntimeError(f"El caso de {line_count} líneas no compila: {result.diagnostics}")
    ordered = sorted(timings_ms)
    return {
        "requested_lines": line_count,
        "actual_lines": len(source.splitlines()),
        "source_bytes": len(source.encode("utf-8")),
        "iterations": iterations,
        "p50_ms": round(statistics.median(ordered), 3),
        "p95_ms": round(statistics.quantiles(ordered, n=100, method="inclusive")[94], 3),
        "min_ms": round(ordered[0], 3),
        "max_ms": round(ordered[-1], 3),
    }


def main() -> int:
    iterations = int(os.environ.get("PSEUDO_STUDIO_BENCHMARK_ITERATIONS", "30"))
    if not 5 <= iterations <= 1000:
        raise ValueError("PSEUDO_STUDIO_BENCHMARK_ITERATIONS debe estar entre 5 y 1000.")
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "targets": [],
        "measurements": [measure(size, iterations) for size in (100, 1000)],
    }
    report_path = ROOT / "reports/compiler-performance.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown = [
        "# Compiler analysis benchmark",
        "",
        f"Generated `{report['generated_at']}` · Python `{report['python']}` · `{report['platform']}` · CPUs `{report['cpu_count']}`",
        "",
        "| Lines | Bytes | Iterations | p50 ms | p95 ms | Min ms | Max ms |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["measurements"]:
        markdown.append(
            f"| {item['actual_lines']} | {item['source_bytes']} | {item['iterations']} | {item['p50_ms']:.3f} | "
            f"{item['p95_ms']:.3f} | {item['min_ms']:.3f} | {item['max_ms']:.3f} |"
        )
    (ROOT / "reports/compiler-performance.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    print("\n".join(markdown))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
