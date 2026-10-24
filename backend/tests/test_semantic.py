import unittest
from pathlib import Path

from backend.compiler.lexer import lex
from backend.compiler.parser import parse
from backend.compiler.semantic import analyze
from backend.compiler.service import compile_source

ROOT = Path(__file__).resolve().parents[2]


def semantic(source: str):
    lexical = lex(source)
    parsed = parse(lexical.tokens)
    return parsed, analyze(parsed.program) if parsed.program else None


class SemanticTests(unittest.TestCase):
    def test_all_official_sources_have_no_semantic_errors(self) -> None:
        for name in "ABCDE":
            source = (ROOT / f"examples/{name}.psc").read_text()
            parsed, result = semantic(source)
            self.assertEqual(parsed.diagnostics, [], name)
            self.assertEqual([item.code for item in result.diagnostics], [], name)

    def test_unknown_name_and_read_before_initialization_are_diagnosed(self) -> None:
        _, unknown = semantic("Inicio\nEscribir total\nFin\n")
        self.assertIn("SEM_UNDEFINED_IDENTIFIER", [item.code for item in unknown.diagnostics])
        self.assertIn("Declare o asigne", unknown.diagnostics[0].hint)
        _, branch = semantic("Inicio\nSi Verdadero Entonces\nx = 1\nFinSi\nEscribir x\nFin\n")
        self.assertIn("SEM_UNINITIALIZED", [item.code for item in branch.diagnostics])
        uninitialized = next(item for item in branch.diagnostics if item.code == "SEM_UNINITIALIZED")
        self.assertIn("antes de leerla", uninitialized.hint)

    def test_both_conditional_paths_initialize_symbol(self) -> None:
        _, result = semantic("Inicio\nSi Verdadero Entonces\nx = 1\nSino\nx = 2\nFinSi\nEscribir x\nFin\n")
        self.assertNotIn("SEM_UNINITIALIZED", [item.code for item in result.diagnostics])

    def test_type_mismatch_constant_step_zero_and_function_arity(self) -> None:
        source = 'Inicio\nx = 1\nx = "texto"\nPara i = 1 Hasta 4 Paso 0 Hacer\nFinPara\nFuncion f(a)\nRetornar a\nFinFuncion\nresultado = f()\nFin\n'
        _, result = semantic(source)
        codes = [item.code for item in result.diagnostics]
        self.assertIn("SEM_TYPE_MISMATCH", codes)
        self.assertIn("SEM_INVALID_STEP", codes)
        self.assertIn("SEM_WRONG_ARITY", codes)

    def test_duplicate_function_names_are_rejected_with_semantic_diagnostic(self) -> None:
        source = "Inicio\nFuncion Repetida()\nRetornar 1\nFinFuncion\nFuncion Repetida()\nRetornar 2\nFinFuncion\nFin\n"
        _, result = semantic(source)
        self.assertIn("SEM_DUPLICATE_FUNCTION", [item.code for item in result.diagnostics])

    def test_scopes_and_symbols_track_references(self) -> None:
        source = "Inicio\nFuncion Doble(n)\nresultado = n * 2\nRetornar resultado\nFinFuncion\nx = Doble(3)\nEscribir x\nFin\n"
        _, result = semantic(source)
        self.assertEqual(result.diagnostics, [])
        x = next(symbol for symbol in result.symbols if symbol.name == "x" and symbol.scope == "global")
        param = next(symbol for symbol in result.symbols if symbol.name == "n" and symbol.scope == "function:Doble")
        self.assertEqual(x.type, "number")
        self.assertGreaterEqual(x.writes, 1)
        self.assertEqual(param.kind, "parameter")
        self.assertGreater(param.reads, 0)

    def test_function_global_dependency_is_checked_at_call_site(self) -> None:
        source = "Inicio\nFuncion Get()\nRetornar total\nFinFuncion\nx = Get()\ntotal = 1\nFin\n"
        _, result = semantic(source)
        self.assertIn("SEM_UNINITIALIZED", [item.code for item in result.diagnostics])

    def test_array_parameter_type_is_inferred_and_scalar_arguments_are_rejected(self) -> None:
        valid = "Inicio\nFuncion Primero(valores)\nRetornar valores[1]\nFinFuncion\nDimension datos[1]\ndatos[1] = 8\nx = Primero(datos)\nFin\n"
        _, valid_result = semantic(valid)
        self.assertEqual(valid_result.diagnostics, [])
        parameter = next(
            item for item in valid_result.symbols if item.scope == "function:Primero" and item.name == "valores"
        )
        self.assertEqual(parameter.type, "array")

        invalid = valid.replace("x = Primero(datos)", "x = Primero(8)")
        _, invalid_result = semantic(invalid)
        self.assertIn("SEM_TYPE_MISMATCH", [item.code for item in invalid_result.diagnostics])

    def test_array_dimensions_must_be_positive_integers(self) -> None:
        for dimension in ("0", "-1", "1.5"):
            with self.subTest(dimension=dimension):
                source = f"Inicio\nDimension datos[{dimension}]\nFin\n"
                _, result = semantic(source)
                self.assertTrue(any(item.code == "SEM_INVALID_DIMENSION" for item in result.diagnostics))
                compiled = compile_source(source)
                self.assertFalse(compiled.translatable)
                self.assertEqual(compiled.artifacts, {})


if __name__ == "__main__":
    unittest.main()
