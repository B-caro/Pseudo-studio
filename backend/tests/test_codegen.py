import ast
import subprocess
import tempfile
import unittest
from pathlib import Path

from backend.compiler.lexer import lex
from backend.compiler.parser import parse
from backend.compiler.semantic import analyze
from backend.generators.codegen import GenerationError, generate

ROOT = Path(__file__).resolve().parents[2]


class CodeGenerationTests(unittest.TestCase):
    def test_all_official_programs_generate_two_parseable_standalone_targets(self) -> None:
        for name in "ABCDE":
            source = (ROOT / f"examples/{name}.psc").read_text()
            parsed = parse(lex(source).tokens)
            semantic = analyze(parsed.program)
            self.assertEqual(semantic.diagnostics, [], name)
            python = generate(parsed.program, semantic.symbols, "python", validated=True)
            javascript = generate(parsed.program, semantic.symbols, "javascript", validated=True)
            with self.subTest(program=name, target="python"):
                ast.parse(python.source)
                self.assertEqual(len(python.artifact_hash), 64)
                self.assertTrue(python.source_map)
                self.assertIn("def __ps_", python.source)
            with self.subTest(program=name, target="javascript"):
                self.assertEqual(len(javascript.artifact_hash), 64)
                self.assertTrue(javascript.source_map)
                with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as file:
                    file.write(javascript.source)
                    file.flush()
                    checked = subprocess.run(
                        ["node", "--check", file.name], capture_output=True, text=True, check=False
                    )
                self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertNotEqual(python.source, javascript.source)

    def test_invalid_semantic_result_cannot_be_generated(self) -> None:
        parsed = parse(lex("Inicio\nEscribir missing\nFin\n").tokens)
        semantic = analyze(parsed.program)
        self.assertTrue(semantic.diagnostics)
        with self.assertRaises(GenerationError):
            generate(parsed.program, semantic.symbols, "python", validated=False)


if __name__ == "__main__":
    unittest.main()
