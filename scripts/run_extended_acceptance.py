#!/usr/bin/env python3
"""Run extended valid and invalid regression programs in the isolated Python/Node runtimes."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.compiler.service import compile_source  # noqa: E402
from backend.runtime.runner import OciRunner  # noqa: E402

EXTENDED = ROOT / "examples/extended"


def source_text(relative_path: str) -> str:
    return (EXTENDED / relative_path).read_text(encoding="utf-8")


def diagnostic_records(result: Any) -> list[dict[str, Any]]:
    return [
        {
            "code": item.code,
            "stage": item.stage,
            "severity": item.severity,
            "line": item.span.start_line,
            "column": item.span.start_column,
            "end_line": item.span.end_line,
            "end_column": item.span.end_column,
            "message": item.message,
        }
        for item in result.diagnostics
    ]


def runtime_error_payload(stderr: str) -> dict[str, Any] | None:
    for line in stderr.splitlines():
        if line.startswith("PSEUDO_RUNTIME_ERROR "):
            try:
                value = json.loads(line.removeprefix("PSEUDO_RUNTIME_ERROR "))
            except json.JSONDecodeError:
                return None
            return value if isinstance(value, dict) else None
    return None


def expected_diagnostics(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"code": item["code"], "stage": item["stage"], "line": item["line"], "column": item["column"]} for item in items
    ]


def compact_diagnostics(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: item[key] for key in ("code", "stage", "line", "column")} for item in items]


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Extended compiler and runtime acceptance",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Result: **{report['passed_checks']}/{report['total_checks']} checks passed**.",
        "",
        "The original A–E fixtures are unchanged. These additional programs exercise more combinations of the public language grammar.",
        "",
        "## Environment",
        "",
        f"- OCI isolation boundary: `{report['sandbox']['status'].get('isolation_boundary')}`",
        f"- Python runtime: `{report['sandbox']['checks']['python'].get('runtime_version')}`",
        f"- Node runtime: `{report['sandbox']['checks']['javascript'].get('runtime_version')}`",
        "",
        "## Valid programs in both runtimes",
        "",
        "| Program / case | Target | Input lines | Status | Exit | Duration ms | Exact stdout | stderr | Source SHA-256 | Artifact SHA-256 |",
        "|---|---|---|---|---:|---:|---|---|---|---|",
    ]
    for item in report["valid_runs"]:
        expected = item["expected_stdout"].replace("\n", "\\n").replace("|", "\\|")
        actual = item["actual_stdout"].replace("\n", "\\n").replace("|", "\\|")
        stderr = item["stderr"].replace("\n", "\\n").replace("|", "\\|")
        lines.append(
            f"| {item['program_id']} / {item['case_id']} | {item['target']} | `{json.dumps(item['inputs'], ensure_ascii=False)}` "
            f"| {item['status']} | {item['exit_code']} | {item['duration_ms']:.2f} | expected `{expected}`, actual `{actual}` "
            f"| `{stderr}` | `{item['source_hash']}` | `{item['artifact_hash']}` |"
        )
    lines.extend(
        [
            "",
            "## Invalid source diagnostics",
            "",
            "| Case | Passed | Expected diagnostic code/stage/span | Actual diagnostics |",
            "|---|---:|---|---|",
        ]
    )
    for item in report["invalid_programs"]:
        lines.append(
            f"| {item['id']} | {item['passed']} | `{json.dumps(item['expected_diagnostics'], ensure_ascii=False)}` "
            f"| `{json.dumps(item['actual_diagnostics'], ensure_ascii=False)}` |"
        )
    lines.extend(
        [
            "",
            "## Controlled runtime failures",
            "",
            "| Case | Target | Inputs | Expected error | Actual status / exit / error | Diagnostic line | Duration ms | Source SHA-256 | Artifact SHA-256 |",
            "|---|---|---|---|---|---:|---:|---|---|",
        ]
    )
    for item in report["runtime_errors"]:
        error_line = item["actual_diagnostic"].get("line") if item["actual_diagnostic"] else None
        lines.append(
            f"| {item['id']} | {item['target']} | `{json.dumps(item['inputs'], ensure_ascii=False)}` "
            f"| {item['expected_error_code']} | {item['status']} / {item['exit_code']} / `{item['error_code']}` "
            f"| {error_line} | {item['duration_ms']:.2f} | `{item['source_hash']}` | `{item['artifact_hash']}` |"
        )
    lines.extend(
        [
            "",
            "## Coverage summary",
            "",
            f"- Valid executions: {report['summary']['valid_runs_passed']}/{report['summary']['valid_runs_total']}.",
            f"- Invalid programs diagnosed at expected spans: {report['summary']['invalid_passed']}/{report['summary']['invalid_total']}.",
            f"- Runtime errors normalized across Python and Node: {report['summary']['runtime_errors_passed']}/{report['summary']['runtime_errors_total']}.",
            "- Features covered: forward and recursive functions, return aliases, parameter typing, strings and Unicode, nested conditionals and loops, precedence, booleans, modulo, negative and fractional arithmetic, dynamic arrays, 1-based bounds, uninitialized values, malformed input, and located diagnostics.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    suite = json.loads((EXTENDED / "cases.json").read_text(encoding="utf-8"))
    runner = OciRunner(timeout_seconds=10.0)
    sandbox = runner.verify_controls()
    if not sandbox["available"]:
        print(json.dumps(sandbox, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    compilations: list[dict[str, Any]] = []
    valid_runs: list[dict[str, Any]] = []
    invalid_programs: list[dict[str, Any]] = []
    runtime_errors: list[dict[str, Any]] = []

    for program in suite["valid_programs"]:
        source = source_text(program["source"])
        result = compile_source(source)
        passed = result.translatable and set(result.artifacts) == {"python", "javascript"}
        compilations.append(
            {
                "program_id": program["id"],
                "passed": passed,
                "translatable": result.translatable,
                "source_hash": result.source_hash,
                "diagnostics": diagnostic_records(result),
            }
        )
        if not passed:
            continue
        for case in program["cases"]:
            for target in ("python", "javascript"):
                artifact = result.artifacts[target]
                execution = runner.run_batch(
                    target, artifact.source, case["inputs"], result.source_hash, artifact.artifact_hash
                )
                passed = (
                    execution.status == "completed"
                    and execution.exit_code == 0
                    and execution.stdout == case["expected_stdout"]
                    and not execution.stderr
                )
                valid_runs.append(
                    {
                        "program_id": program["id"],
                        "case_id": case["id"],
                        "target": target,
                        "inputs": case["inputs"],
                        "expected_stdout": case["expected_stdout"],
                        "actual_stdout": execution.stdout,
                        "stderr": execution.stderr,
                        "status": execution.status,
                        "exit_code": execution.exit_code,
                        "duration_ms": execution.duration_ms,
                        "source_hash": result.source_hash,
                        "artifact_hash": artifact.artifact_hash,
                        "runtime_version": execution.runtime_version,
                        "error_code": execution.error_code,
                        "passed": passed,
                    }
                )
                print(
                    f"{'PASS' if passed else 'FAIL'} {program['id']} {case['id']} {target} {execution.duration_ms:.1f}ms"
                )

    for case in suite["invalid_programs"]:
        source = source_text(case["source"])
        result = compile_source(source)
        actual = compact_diagnostics(diagnostic_records(result))
        expected = expected_diagnostics(case["expected_diagnostics"])
        passed = not result.translatable and not result.artifacts and actual == expected
        invalid_programs.append(
            {
                "id": case["id"],
                "passed": passed,
                "source_hash": result.source_hash,
                "expected_diagnostics": expected,
                "actual_diagnostics": actual,
                "diagnostic_messages": diagnostic_records(result),
            }
        )
        print(f"{'PASS' if passed else 'FAIL'} {case['id']} diagnostics {actual}")

    for case in suite["runtime_error_programs"]:
        source = source_text(case["source"])
        result = compile_source(source)
        if not result.translatable:
            runtime_errors.append(
                {
                    "id": case["id"],
                    "target": "both",
                    "inputs": case["inputs"],
                    "expected_error_code": case["error_code"],
                    "status": "compile_error",
                    "exit_code": None,
                    "error_code": None,
                    "duration_ms": 0.0,
                    "source_hash": result.source_hash,
                    "artifact_hash": None,
                    "actual_diagnostic": None,
                    "stderr": "",
                    "passed": False,
                }
            )
            continue
        for target in ("python", "javascript"):
            artifact = result.artifacts[target]
            execution = runner.run_batch(
                target, artifact.source, case["inputs"], result.source_hash, artifact.artifact_hash
            )
            payload = runtime_error_payload(execution.stderr)
            passed = (
                execution.status == "runtime_error"
                and execution.exit_code == 70
                and execution.error_code == case["error_code"]
                and payload is not None
                and payload.get("code") == case["error_code"]
                and payload.get("line") == case["error_line"]
                and execution.stdout == ""
            )
            runtime_errors.append(
                {
                    "id": case["id"],
                    "target": target,
                    "inputs": case["inputs"],
                    "expected_error_code": case["error_code"],
                    "expected_error_line": case["error_line"],
                    "status": execution.status,
                    "exit_code": execution.exit_code,
                    "error_code": execution.error_code,
                    "duration_ms": execution.duration_ms,
                    "source_hash": result.source_hash,
                    "artifact_hash": artifact.artifact_hash,
                    "runtime_version": execution.runtime_version,
                    "actual_diagnostic": payload,
                    "stderr": execution.stderr,
                    "passed": passed,
                }
            )
            print(
                f"{'PASS' if passed else 'FAIL'} {case['id']} {target} {execution.error_code} {execution.duration_ms:.1f}ms"
            )

    all_checks = [*compilations, *valid_runs, *invalid_programs, *runtime_errors]
    passed_checks = sum(1 for item in all_checks if item["passed"])
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "authority": suite["authority"],
        "sandbox": sandbox,
        "total_checks": len(all_checks),
        "passed_checks": passed_checks,
        "failed_checks": len(all_checks) - passed_checks,
        "summary": {
            "valid_compilations_passed": sum(1 for item in compilations if item["passed"]),
            "valid_compilations_total": len(compilations),
            "valid_runs_passed": sum(1 for item in valid_runs if item["passed"]),
            "valid_runs_total": len(valid_runs),
            "invalid_passed": sum(1 for item in invalid_programs if item["passed"]),
            "invalid_total": len(invalid_programs),
            "runtime_errors_passed": sum(1 for item in runtime_errors if item["passed"]),
            "runtime_errors_total": len(runtime_errors),
        },
        "compilations": compilations,
        "valid_runs": valid_runs,
        "invalid_programs": invalid_programs,
        "runtime_errors": runtime_errors,
    }
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "extended-acceptance-results.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (reports / "extended-acceptance-results.md").write_text(markdown_report(report), encoding="utf-8")
    print(
        f"Extended acceptance: {passed_checks}/{len(all_checks)} checks passed. "
        "Reports: reports/extended-acceptance-results.json and .md"
    )
    return 0 if passed_checks == len(all_checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
