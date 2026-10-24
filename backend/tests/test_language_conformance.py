import unittest

from backend.compiler.lexer import lex
from backend.compiler.parser import parse
from backend.compiler.semantic import analyze
from backend.compiler.service import compile_source

VALID_EXTENSION_PROGRAM = r"""Inicio
// Las reglas soportan Unicode, escapes y comentarios de línea.
etiqueta = "café\n"
texto = "valor: "
valores = Duplicar(3)
Dimension datos[2]
datos[1] = -3
datos[2] = 5
i = 1
total = 0
Mientras i <= 2 Hacer
    total = total + datos[i]
    i = i + 1
FinMientras
Si No (total == 0) O Verdadero Y Falso Entonces
    Escribir etiqueta, texto, total Modulo 2
Sino
    Escribir "cero"
FinSi
Para k = 3 Hasta 1 Paso -1 Hacer
    Escribir k
FinPara
Funcion Duplicar(numero)
    resultado = numero * 2
    Retornar resultado
FinFuncion
Fin
"""


class LanguageConformanceTests(unittest.TestCase):
    def test_extensions_and_forward_function_call_pass_all_static_phases(self) -> None:
        lexical = lex(VALID_EXTENSION_PROGRAM)
        self.assertEqual(lexical.diagnostics, [])
        parsed = parse(lexical.tokens)
        self.assertEqual(parsed.diagnostics, [])
        result = analyze(parsed.program)
        self.assertEqual(result.diagnostics, [])

    def test_syntax_errors_are_located_and_do_not_emit_ast_as_valid(self) -> None:
        for source, expected in [
            ("Inicio\nx = (1 + 2\nFin\n", "SYN_UNEXPECTED_TOKEN"),
            ("Inicio\nSi Verdadero Entonces\nEscribir 1\nFin\n", "SYN_UNEXPECTED_TOKEN"),
        ]:
            parsed = parse(lex(source).tokens)
            self.assertTrue(any(item.code == expected for item in parsed.diagnostics))

    def test_reserved_words_are_case_insensitive_and_cannot_be_names(self) -> None:
        lexical = lex("Inicio\nSi = 1\nFin\n")
        parsed = parse(lexical.tokens)
        self.assertTrue(parsed.diagnostics)

    def test_deep_expression_and_long_program_are_handled_without_parser_pathology(self) -> None:
        nested = "(" * 120 + "7" + ")" * 120
        statements = "".join("Escribir 1\n" for _ in range(1000))
        source = f"Inicio\nEscribir {nested}\n{statements}Fin\n"
        result = compile_source(source)
        self.assertTrue(result.translatable, [item.to_dict() for item in result.diagnostics])
        self.assertEqual(set(result.artifacts), {"python", "javascript"})

    def test_many_invalid_tokens_recover_with_bounded_diagnostics(self) -> None:
        source = "Inicio\n" + "@\n" * 1000 + "Fin\n"
        result = compile_source(source)
        self.assertFalse(result.translatable)
        self.assertTrue(result.diagnostics)
        self.assertLessEqual(len(result.diagnostics), 2000)

    def test_multiple_nested_errors_recover_and_keep_hints_with_exact_spans(self) -> None:
        source = "Inicio\nSi Verdadero Entonces\nEscribir @\nSino\nx =\nFinSi\nFin\n"
        result = compile_source(source)
        self.assertFalse(result.translatable)
        self.assertEqual(result.artifacts, {})
        self.assertIn("LEX_INVALID_CHAR", [item.code for item in result.diagnostics])
        syntax_errors = [item for item in result.diagnostics if item.stage == "syntax"]
        self.assertEqual([item.span.start_line for item in syntax_errors], [3, 5])
        self.assertTrue(all(item.hint for item in result.diagnostics))

    def test_python_spans_remain_codepoint_offsets_after_non_bmp_unicode(self) -> None:
        source = 'Inicio\nEscribir "😀"\nEscribir falta\nFin\n'
        result = compile_source(source, targets=())
        diagnostic = next(item for item in result.diagnostics if item.code == "SEM_UNDEFINED_IDENTIFIER")
        self.assertEqual(source[diagnostic.span.start : diagnostic.span.end], "falta")


if __name__ == "__main__":
    unittest.main()
