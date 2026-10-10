from backend.test_service.differential import compare_targets


def _run(target: str, stdout: str, stderr: str = "", *, status: str = "completed", exit_code: int = 0) -> dict:
    return {
        "case_id": "case-1",
        "target": target,
        "actual_stdout": stdout,
        "stderr": stderr,
        "status": status,
        "exit_code": exit_code,
    }


def test_comparison_preserves_raw_diffs_and_only_normalizes_line_endings() -> None:
    [comparison] = compare_targets(
        [
            _run("python", "line one\r\nline two\r\n", "warning\r\n"),
            _run("javascript", "line one\nline two\n", "warning\n"),
        ]
    )
    assert comparison["raw_stdout_match"] is False
    assert comparison["normalized_stdout_match"] is True
    assert comparison["raw_stderr_match"] is False
    assert comparison["normalized_stderr_match"] is True
    assert comparison["equivalent"] is True
    assert "python.stdout" in comparison["stdout_diff"]


def test_comparison_reports_content_runtime_and_missing_target_divergence() -> None:
    [different, missing] = compare_targets(
        [
            _run("python", "actual\n"),
            _run("javascript", "different\n", status="runtime_error", exit_code=1),
            {**_run("python", "only python\n"), "case_id": "case-2"},
        ]
    )
    assert different["raw_stdout_match"] is False
    assert different["normalized_stdout_match"] is False
    assert different["execution_match"] is False
    assert different["equivalent"] is False
    assert "different" in different["stdout_diff"]
    assert missing == {
        "case_id": "case-2",
        "equivalent": False,
        "reason": "MISSING_TARGET",
        "targets": ["python"],
    }
