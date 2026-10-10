#!/usr/bin/env python3
"""Regenerate real codegen golden files from the academic source programs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.compiler.service import compile_source  # noqa: E402


def main() -> int:
    destination = ROOT / "backend/tests/snapshots"
    destination.mkdir(parents=True, exist_ok=True)
    for program in "ABCDE":
        source = (ROOT / "examples" / f"{program}.psc").read_text(encoding="utf-8")
        result = compile_source(source)
        if not result.translatable:
            raise RuntimeError(f"No se puede crear snapshot: {program} tiene diagnósticos.")
        for target, extension in (("python", ".py"), ("javascript", ".js")):
            path = destination / f"{program}{extension}.snapshot"
            path.write_text(result.artifacts[target].source, encoding="utf-8", newline="\n")
            print(f"Generated {path.relative_to(ROOT)} · {result.artifacts[target].artifact_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
