#!/usr/bin/env python3
"""Run the manual Phase 1 A/B translations with their official inputs."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS = ROOT / "examples/phase1-translations"
OFFICIAL = json.loads((ROOT / "examples/official-cases.json").read_text(encoding="utf-8"))
NODE = shutil.which("node")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# A/B manual translation acceptance",
        "",
        f"Generated: **{report['generated_at']}**",
        f"Result: **{report['passed_runs']}/{report['total_runs']} runs passed**.",
        "",
        f"- Python: {report['runtimes']['python']}",
        f"- Node: {report['runtimes']['node']}",
        "- Input delivery: all case lines are written to stdin together in one batch.",
        "- This host run does not claim OCI isolation; the sandbox status is recorded separately.",
        "",
        "| Case | Target | Input batch | Exit | Duration ms | Exact stdout | stderr | Source SHA-256 |",
        "|---|---|---|---:|---:|---|---|---|",
    ]
    for run in report["runs"]:
        expected = run["expected_stdout"].replace("\n", "\\n").replace("|", "\\|")
        actual = run["actual_stdout"].replace("\n", "\\n").replace("|", "\\|")
        stderr = run["stderr"].replace("\n", "\\n").replace("|", "\\|")
        lines.append(
            f"| {run['case_id']} | {run['target']} | {json.dumps(run['inputs'], ensure_ascii=False)} "
            f"| {run['exit_code']} | {run['duration_ms']:.2f} | expected {expected}, actual {actual} "
            f"| {stderr} | {run['source_sha256']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    if NODE is None:
        print("Node.js is required to run the JavaScript manual translations.", file=sys.stderr)
        return 2

    python_version = subprocess.run(
        [sys.executable, "--version"], capture_output=True, text=True, check=True, timeout=5
    )
    node_version = subprocess.run([NODE, "--version"], capture_output=True, text=True, check=True, timeout=5)
    versions = {"python": (python_version.stdout or python_version.stderr).strip(), "node": node_version.stdout.strip()}
    runs: list[dict[str, Any]] = []
    for case in OFFICIAL["cases"]:
        if case["program"] not in {"A", "B"}:
            continue
        prompts = OFFICIAL["prompt_templates"][case["program"]]
        expected_stdout = "\n".join([*prompts, case["expected_tail"]]) + "\n"
        input_batch = "\n".join(case["inputs"]) + "\n"
        for target, suffix, executable in (
            ("python", "py", sys.executable),
            ("javascript", "js", NODE),
        ):
            source_path = TRANSLATIONS / f"{case['program']}-{target}.{suffix}"
            started = time.monotonic()
            result = subprocess.run(
                [executable, str(source_path)],
                input=input_batch,
                text=True,
                capture_output=True,
                check=False,
                timeout=5,
            )
            duration_ms = (time.monotonic() - started) * 1000
            passed = result.returncode == 0 and result.stdout == expected_stdout and result.stderr == ""
            runs.append(
                {
                    "case_id": case["id"],
                    "program": case["program"],
                    "target": target,
                    "inputs": case["inputs"],
                    "expected_stdout": expected_stdout,
                    "actual_stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.returncode,
                    "duration_ms": duration_ms,
                    "source_sha256": sha256(source_path.read_bytes()),
                    "passed": passed,
                }
            )
            print(f"{'PASS' if passed else 'FAIL'} {case['id']} {target} {duration_ms:.1f}ms")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runtimes": versions,
        "input_mode": "stdin batch",
        "total_runs": len(runs),
        "passed_runs": sum(run["passed"] for run in runs),
        "failed_runs": sum(not run["passed"] for run in runs),
        "runs": runs,
    }
    report_dir = ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    (report_dir / "phase1-manual-acceptance.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (report_dir / "phase1-manual-acceptance.md").write_text(markdown(report), encoding="utf-8")
    print(f"Manual A/B result: {report['passed_runs']}/{report['total_runs']}.")
    return 0 if report["failed_runs"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
