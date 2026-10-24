import json
import unittest
from pathlib import Path

from backend.compiler.lexer import lex
from backend.compiler.model import Assign, Binary, Function, If, serialize
from backend.compiler.parser import parse

ROOT = Path(__file__).resolve().parents[2]


class ParserTests(unittest.TestCase):
    def test_all_official_sources_parse_without_syntax_diagnostics(self) -> None:
        for name in "ABCDE":
            source = (ROOT / f"examples/{name}.psc").read_text()
            lexical = lex(source)
            parsed = parse(lexical.tokens)
            self.assertEqual(lexical.diagnostics, [], name)
            self.assertEqual(parsed.diagnostics, [], name)
            self.assertIsNotNone(parsed.program, name)

    def test_pratt_parser_preserves_precedence_and_parentheses(self) -> None:
        source = "Inicio\nx = 1 + 2 * 3\ntotal = (1 + 2) * 3\nFin\n"
        parsed = parse(lex(source).tokens)
        self.assertEqual(parsed.diagnostics, [])
        first, second = parsed.program.body
        self.assertIsInstance(first, Assign)
        self.assertIsInstance(first.value, Binary)
        self.assertEqual(first.value.operator, "+")
        self.assertEqual(first.value.right.operator, "*")
        self.assertEqual(second.value.operator, "*")
        self.assertEqual(second.value.left.operator, "+")

    def test_nested_blocks_and_function_return_alias_are_typed_nodes(self) -> None:
        source = (ROOT / "examples/E.psc").read_text()
        parsed = parse(lex(source).tokens)
        functions = [item for item in parsed.program.body if isinstance(item, Function)]
        self.assertEqual([item.name for item in functions], ["CalcularArea", "ClasificarArea"])
        self.assertEqual([item.return_alias for item in functions], ["area", "clasificacion"])
        inner_if = next(item for item in functions[1].body if isinstance(item, If))
        self.assertEqual(len(inner_if.else_body), 1)

    def test_json_serialization_contains_spans_and_no_python_objects(self) -> None:
        parsed = parse(lex('Inicio\nEscribir "ok"\nFin\n').tokens)
        value = serialize(parsed.program)
        encoded = json.dumps(value, ensure_ascii=False)
        self.assertIn('"kind": "Program"', encoded)
        self.assertIn('"start_line": 2', encoded)

    def test_missing_block_terminator_reports_syntax_error_and_returns(self) -> None:
        parsed = parse(lex("Inicio\nSi Verdadero Entonces\nEscribir 1\nFin\n").tokens)
        self.assertTrue(any(item.code == "SYN_UNEXPECTED_TOKEN" for item in parsed.diagnostics))
        self.assertLess(parsed.diagnostics[0].span.start_line, 5)
        self.assertIn("FinSi", parsed.diagnostics[0].hint)


if __name__ == "__main__":
    unittest.main()
