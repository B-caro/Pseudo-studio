import hashlib
import unittest
from pathlib import Path

from backend.compiler.service import compile_source

ROOT = Path(__file__).resolve().parents[2]


class CompilerServiceTests(unittest.TestCase):
    def test_official_sources_produce_real_two_target_artifacts(self) -> None:
        for name in "ABCDE":
            source = (ROOT / f"examples/{name}.psc").read_text()
            result = compile_source(source)
            self.assertTrue(result.translatable, [item.to_dict() for item in result.diagnostics])
            self.assertEqual(set(result.artifacts), {"python", "javascript"})
            self.assertEqual(result.source_hash, hashlib.sha256(source.encode()).hexdigest())
            self.assertNotEqual(result.artifacts["python"].artifact_hash, result.artifacts["javascript"].artifact_hash)

    def test_invalid_source_has_diagnostics_and_no_artifacts(self) -> None:
        result = compile_source("Inicio\nEscribir missing\nFin\n")
        self.assertFalse(result.translatable)
        self.assertEqual(result.artifacts, {})
        self.assertIn("SEM_UNDEFINED_IDENTIFIER", [item.code for item in result.diagnostics])

    def test_source_edit_changes_hash_and_generated_artifacts(self) -> None:
        original = "Inicio\nx = 2\nEscribir x\nFin\n"
        changed = "Inicio\nx = 3\nEscribir x\nFin\n"
        first, second = compile_source(original), compile_source(changed)
        self.assertNotEqual(first.source_hash, second.source_hash)
        self.assertNotEqual(first.artifacts["python"].artifact_hash, second.artifacts["python"].artifact_hash)
        self.assertNotEqual(first.artifacts["javascript"].artifact_hash, second.artifacts["javascript"].artifact_hash)


if __name__ == "__main__":
    unittest.main()
