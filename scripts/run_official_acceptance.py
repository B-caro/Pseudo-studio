#!/usr/bin/env python3
"""Run all official A-E datasets through the isolated Python and Node OCI images."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.compiler.service import compile_source  # noqa: E402
from backend.runtime.runner import OciRunner  # noqa: E402
from backend.test_service.official import official_stdout  # noqa: E402


def main() -> int:
    cases_file = ROOT / "examples/official-cases.json"
    cases = json.loads(cases_file.read_text(encoding="utf-8"))
    runner = OciRunner()
    controls = runner.verify_controls()
    if not controls["available"]:
        print(json.dumps(controls, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    compiled = {}
    for program, relative in cases["source_files"].items():
        source = (ROOT / relative).read_text(encoding="utf-8")
        result = compile_source(source)
        if not result.translatable:
            print(f"{program} compilation failed: {[item.to_dict() for item in result.diagnostics]}", file=sys.stderr)
            return 1
        compiled[program] = (source, result)

    runs = []
    for case in cases["cases"]:
        source, result = compiled[case["program"]]
        expected = official_stdout(case["program"], case["inputs"], case["expected_tail"])
        for target in ("python", "javascript"):
            artifact = result.artifacts[target]
            execution = runner.run_batch(
                target, artifact.source, case["inputs"], result.source_hash, artifact.artifact_hash
            )
            record = {
                "case_id": case["id"],
                "program": case["program"],
                "target": target,
                "inputs": case["inputs"],
                "expected_stdout": expected,
                "actual_stdout": execution.stdout,
                "stderr": execution.stderr,
                "status": execution.status,
                "exit_code": execution.exit_code,
                "duration_ms": execution.duration_ms,
                "source_hash": result.source_hash,
                "artifact_hash": artifact.artifact_hash,
                "compiler_version": result.compiler_version,
                "runtime_version": execution.runtime_version,
                "error_code": execution.error_code,
                "passed": execution.status == "completed"
                and execution.exit_code == 0
                and execution.stdout == expected
                and not execution.stderr,
            }
            runs.append(record)
            print(f"{'PASS' if record['passed'] else 'FAIL'} {case['id']} {target} {execution.duration_ms:.1f}ms")

    passed = sum(1 for record in runs if record["passed"])
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sandbox": controls,
        "total": len(runs),
        "passed": passed,
        "failed": len(runs) - passed,
        "runs": runs,
    }
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "acceptance-results.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Official A–E acceptance runs",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Result: **{passed}/{len(runs)} passed** (real Python/Node OCI executions).",
        "",
        "| Case | Target | Status | Exit | Duration ms | Source SHA-256 | Artifact SHA-256 | Stdout exact | stderr |",
        "|---|---|---|---:|---:|---|---|---|---|",
    ]
    for item in runs:
        stdout = item["actual_stdout"].replace("\n", "\\n").replace("|", "\\|")
        stderr = item["stderr"].replace("\n", "\\n").replace("|", "\\|")
        lines.append(
            f"| {item['case_id']} | {item['target']} | {item['status']} | {item['exit_code']} | "
            f"{item['duration_ms']:.2f} | `{item['source_hash']}` | `{item['artifact_hash']}` | `{stdout}` | `{stderr}` |"
        )
    (reports / "acceptance-results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Official result: {passed}/{len(runs)}. Reports: reports/acceptance-results.json and .md")
    return 0 if passed == len(runs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
