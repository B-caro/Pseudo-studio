import unittest

from backend.compiler.lexer import lex


class LexerTests(unittest.TestCase):
    def test_compound_operators_precede_single_operators(self) -> None:
        result = lex("a >= 2 Y b != 3")
        self.assertEqual([token.lexeme for token in result.tokens[:-1]], ["a", ">=", "2", "Y", "b", "!=", "3"])
        self.assertEqual(result.diagnostics, [])

    def test_unicode_identifiers_are_nfc_and_case_sensitive(self) -> None:
        result = lex("área Area a\u0301rea")
        values = [token.value for token in result.tokens if token.kind == "IDENT"]
        self.assertEqual(values, ["área", "Area", "área"])

    def test_string_escapes_and_invalid_escape_have_spans(self) -> None:
        result = lex('"uno\\n\\t\\"\\\\" "malo\\q"')
        strings = [token for token in result.tokens if token.kind == "STRING"]
        self.assertEqual(strings[0].value, 'uno\n\t"\\')
        self.assertEqual([item.code for item in result.diagnostics], ["LEX_INVALID_ESCAPE"])
        self.assertGreater(result.diagnostics[0].span.end, result.diagnostics[0].span.start)

    def test_comments_preserve_newlines_and_offsets(self) -> None:
        result = lex("x = 1 // nota\nEscribir x\n")
        self.assertEqual([token.kind for token in result.tokens].count("NEWLINE"), 2)
        escribir = next(token for token in result.tokens if token.lexeme == "Escribir")
        self.assertEqual((escribir.span.start_line, escribir.span.start_column), (2, 1))

    def test_bad_characters_and_unterminated_strings_are_diagnostics(self) -> None:
        result = lex('Escribir @\nEscribir "no termina')
        self.assertEqual([item.code for item in result.diagnostics], ["LEX_INVALID_CHAR", "LEX_UNTERMINATED_STRING"])
        self.assertEqual((result.diagnostics[0].span.start_line, result.diagnostics[0].span.start_column), (1, 10))

    def test_numbers_are_decimal_without_exponent_or_nonfinite_literals(self) -> None:
        result = lex("12 3.25 4e2")
        self.assertEqual([token.lexeme for token in result.tokens if token.kind == "NUMBER"], ["12", "3.25", "4"])
        self.assertEqual([token.value for token in result.tokens if token.kind == "IDENT"], ["e2"])
        self.assertEqual(result.diagnostics, [])

    def test_numeric_literals_use_ascii_digits(self) -> None:
        result = lex("١")
        self.assertEqual([item.code for item in result.diagnostics], ["LEX_INVALID_CHAR"])
        self.assertEqual([token.kind for token in result.tokens], ["EOF"])


if __name__ == "__main__":
    unittest.main()
