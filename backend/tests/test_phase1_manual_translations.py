from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRANSLATIONS = ROOT / "examples/phase1-translations"
NODE = shutil.which("node")
OFFICIAL = json.loads((ROOT / "examples/official-cases.json").read_text(encoding="utf-8"))


class PhaseOneManualTranslationsTests(unittest.TestCase):
    def _run(self, source: str, target: str, stdin: str) -> subprocess.CompletedProcess[str]:
        path = TRANSLATIONS / source
        command = [sys.executable, str(path)] if target == "python" else [NODE, str(path)]
        return subprocess.run(command, input=stdin, text=True, capture_output=True, check=False, timeout=5)

    def test_program_a_accepts_all_inputs_in_one_stdin_write(self) -> None:
        cases = [case for case in OFFICIAL["cases"] if case["program"] == "A"]
        expected_prompts = "\n".join(OFFICIAL["prompt_templates"]["A"]) + "\n"
        for target in ("python", "javascript"):
            for case in cases:
                stdin = "\n".join(case["inputs"]) + "\n"
                with self.subTest(target=target, case=case["id"]):
                    result = self._run(f"A-{target}.{'py' if target == 'python' else 'js'}", target, stdin)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, expected_prompts + case["expected_tail"] + "\n")
                    self.assertEqual(result.stderr, "")

    def test_program_b_reaches_all_nested_conditional_branches(self) -> None:
        cases = [case for case in OFFICIAL["cases"] if case["program"] == "B"]
        expected_prompts = "\n".join(OFFICIAL["prompt_templates"]["B"]) + "\n"
        for target in ("python", "javascript"):
            for case in cases:
                stdin = "\n".join(case["inputs"]) + "\n"
                with self.subTest(target=target, case=case["id"]):
                    result = self._run(f"B-{target}.{'py' if target == 'python' else 'js'}", target, stdin)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, expected_prompts + case["expected_tail"] + "\n")
                    self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
