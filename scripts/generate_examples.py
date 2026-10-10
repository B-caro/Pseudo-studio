#!/usr/bin/env python3
"""Generate real Python/JavaScript artifacts from the A-E source fixtures."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.compiler.service import compile_source  # noqa: E402


def main() -> int:
    output = ROOT / "reports/generated"
    output.mkdir(parents=True, exist_ok=True)
    entries = []
    for name in "ABCDE":
        source_path = ROOT / f"examples/{name}.psc"
        source = source_path.read_text(encoding="utf-8")
        result = compile_source(source)
        if not result.translatable:
            print(f"{name}: compile failed", file=sys.stderr)
            for diagnostic in result.diagnostics:
                print(f"{diagnostic.code}: {diagnostic.message}", file=sys.stderr)
            return 1
        artifacts = []
        for target in ("python", "javascript"):
            artifact = result.artifacts[target]
            path = output / f"{name}{artifact.extension}"
            path.write_text(artifact.source, encoding="utf-8", newline="\n")
            map_path = output / f"{name}{artifact.extension}.map.json"
            map_path.write_text(json.dumps(artifact.source_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            artifacts.append(
                {
                    "target": target,
                    "path": path.relative_to(ROOT).as_posix(),
                    "source_map": map_path.relative_to(ROOT).as_posix(),
                    "artifact_hash": artifact.artifact_hash,
                }
            )
        entries.append(
            {
                "program": name,
                "source_path": source_path.relative_to(ROOT).as_posix(),
                "source_hash": result.source_hash,
                "compiler_version": result.compiler_version,
                "artifacts": artifacts,
            }
        )
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "compiler_version": entries[0]["compiler_version"] if entries else None,
        "execution_status": "not_executed",
        "programs": entries,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(entries) * 2} artifacts from the compiler pipeline in {output.relative_to(ROOT)}")
    print("Execution status: not_executed (sandbox availability is a separate gate).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
