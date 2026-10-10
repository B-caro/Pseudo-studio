from __future__ import annotations

import difflib
from collections import defaultdict
from typing import Any


def _normalize_newlines(value: str) -> str:
    """Normalize platform line endings while preserving all other differences."""
    return value.replace("\r\n", "\n").replace("\r", "\n")


def compare_targets(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compare actual Python and Node executions without hiding raw output differences."""
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for run in runs:
        grouped[run["case_id"]][run["target"]] = run

    comparisons = []
    for case_id, targets in grouped.items():
        python = targets.get("python")
        javascript = targets.get("javascript")
        if python is None or javascript is None:
            comparisons.append(
                {
                    "case_id": case_id,
                    "equivalent": False,
                    "reason": "MISSING_TARGET",
                    "targets": sorted(targets),
                }
            )
            continue

        python_stdout = python["actual_stdout"]
        javascript_stdout = javascript["actual_stdout"]
        python_stderr = python["stderr"]
        javascript_stderr = javascript["stderr"]
        raw_stdout_match = python_stdout == javascript_stdout
        normalized_stdout_match = _normalize_newlines(python_stdout) == _normalize_newlines(javascript_stdout)
        raw_stderr_match = python_stderr == javascript_stderr
        normalized_stderr_match = _normalize_newlines(python_stderr) == _normalize_newlines(javascript_stderr)
        execution_match = python["status"] == javascript["status"] and python["exit_code"] == javascript["exit_code"]
        comparisons.append(
            {
                "case_id": case_id,
                "raw_stdout_match": raw_stdout_match,
                "normalized_stdout_match": normalized_stdout_match,
                "raw_stderr_match": raw_stderr_match,
                "normalized_stderr_match": normalized_stderr_match,
                "execution_match": execution_match,
                "equivalent": normalized_stdout_match and normalized_stderr_match and execution_match,
                "stdout_diff": ""
                if raw_stdout_match
                else "\n".join(
                    difflib.unified_diff(
                        [repr(python_stdout)],
                        [repr(javascript_stdout)],
                        fromfile="python.stdout",
                        tofile="javascript.stdout",
                        lineterm="",
                    )
                ),
                "stderr_diff": ""
                if raw_stderr_match
                else "\n".join(
                    difflib.unified_diff(
                        [repr(python_stderr)],
                        [repr(javascript_stderr)],
                        fromfile="python.stderr",
                        tofile="javascript.stderr",
                        lineterm="",
                    )
                ),
            }
        )
    return comparisons
