from __future__ import annotations

import json
import unittest
from pathlib import Path

from backend.compiler.service import compile_source
from backend.runtime.runner import OciRunner

ROOT = Path(__file__).resolve().parents[2]
EXTENDED = ROOT / "examples/extended"
CASES = json.loads((EXTENDED / "cases.json").read_text(encoding="utf-8"))


def read_source(relative_path: str) -> str:
    return (EXTENDED / relative_path).read_text(encoding="utf-8")


def runtime_error_payload(stderr: str) -> dict[str, object]:
    for line in stderr.splitlines():
        if line.startswith("PSEUDO_RUNTIME_ERROR "):
            return json.loads(line.removeprefix("PSEUDO_RUNTIME_ERROR "))
    raise AssertionError(f"No se encontró PSEUDO_RUNTIME_ERROR en stderr: {stderr!r}")


class ExtendedCompilationTests(unittest.TestCase):
    def test_complex_valid_programs_generate_both_artifacts(self) -> None:
        for program in CASES["valid_programs"]:
            with self.subTest(program=program["id"]):
                source = read_source(program["source"])
                result = compile_source(source)
                self.assertTrue(result.translatable, [item.to_dict() for item in result.diagnostics])
                self.assertEqual(set(result.artifacts), {"python", "javascript"})
                self.assertEqual(result.phases["generation"]["status"], "ok")
                for artifact in result.artifacts.values():
                    self.assertTrue(artifact.source)
                    self.assertTrue(artifact.program_source)
                    self.assertTrue(artifact.source_map)

    def test_invalid_programs_report_expected_codes_stages_and_spans(self) -> None:
        for case in CASES["invalid_programs"]:
            with self.subTest(case=case["id"]):
                result = compile_source(read_source(case["source"]))
                self.assertFalse(result.translatable)
                self.assertEqual(result.artifacts, {})
                actual = [
                    {
                        "code": item.code,
                        "stage": item.stage,
                        "line": item.span.start_line,
                        "column": item.span.start_column,
                    }
                    for item in result.diagnostics
                ]
                self.assertEqual(actual, case["expected_diagnostics"])


class ExtendedRuntimeIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = OciRunner(timeout_seconds=10.0)
        controls = cls.runner.verify_controls()
        if not controls["available"]:
            raise RuntimeError(f"Secure OCI runtime is required for extended integration tests: {controls}")

    def test_complex_program_cases_match_expected_stdout_in_python_and_node(self) -> None:
        for program in CASES["valid_programs"]:
            source = read_source(program["source"])
            compiled = compile_source(source)
            self.assertTrue(compiled.translatable, [item.to_dict() for item in compiled.diagnostics])
            for case in program["cases"]:
                for target in ("python", "javascript"):
                    with self.subTest(program=program["id"], case=case["id"], target=target):
                        artifact = compiled.artifacts[target]
                        result = self.runner.run_batch(
                            target,
                            artifact.source,
                            case["inputs"],
                            compiled.source_hash,
                            artifact.artifact_hash,
                        )
                        self.assertEqual(
                            (result.status, result.exit_code, result.stdout, result.stderr),
                            ("completed", 0, case["expected_stdout"], ""),
                        )

    def test_dynamic_runtime_errors_are_normalized_in_both_targets(self) -> None:
        for case in CASES["runtime_error_programs"]:
            source = read_source(case["source"])
            compiled = compile_source(source)
            self.assertTrue(compiled.translatable, [item.to_dict() for item in compiled.diagnostics])
            for target in ("python", "javascript"):
                with self.subTest(case=case["id"], target=target):
                    artifact = compiled.artifacts[target]
                    result = self.runner.run_batch(
                        target,
                        artifact.source,
                        case["inputs"],
                        compiled.source_hash,
                        artifact.artifact_hash,
                    )
                    payload = runtime_error_payload(result.stderr)
                    self.assertEqual(
                        (result.status, result.exit_code, result.error_code), ("runtime_error", 70, case["error_code"])
                    )
                    self.assertEqual(payload["code"], case["error_code"])
                    self.assertEqual(payload["line"], case["error_line"])
                    self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
