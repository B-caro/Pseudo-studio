"""Unicode-aware lexer for the Pseudo / Studio source language."""

from __future__ import annotations

import math
import unicodedata
from dataclasses import dataclass

from .model import Diagnostic, Span, Token

KEYWORDS = {
    "inicio",
    "fin",
    "escribir",
    "leer",
    "leertexto",
    "si",
    "entonces",
    "sino",
    "finsi",
    "para",
    "hasta",
    "paso",
    "hacer",
    "finpara",
    "dimension",
    "mientras",
    "finmientras",
    "funcion",
    "finfuncion",
    "retornar",
    "y",
    "o",
    "no",
    "verdadero",
    "falso",
    "modulo",
}
SINGLE_OPERATORS = {"+", "-", "*", "/", "%", "=", "<", ">"}
DOUBLE_OPERATORS = {"==", "!=", "<=", ">="}
PUNCTUATION = {"(", ")", "[", "]", ","}


@dataclass(slots=True)
class LexResult:
    tokens: list[Token]
    diagnostics: list[Diagnostic]


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.length = len(source)
        self.offset = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []
        self.diagnostics: list[Diagnostic] = []

    def scan(self) -> LexResult:
        while self.offset < self.length:
            char = self.source[self.offset]
            if char in " \t\f\v":
                self._advance()
            elif char in "\r\n":
                self._newline()
            elif char == "/" and self._peek(1) == "/":
                self._comment()
            elif char == '"':
                self._string()
            elif char.isascii() and char.isdigit():
                self._number()
            elif char == "." and self._peek(1).isascii() and self._peek(1).isdigit():
                self._number()
            elif self._is_identifier_start(char):
                self._identifier()
            elif self.source[self.offset : self.offset + 2] in DOUBLE_OPERATORS:
                self._operator(self.source[self.offset : self.offset + 2], 2)
            elif char in SINGLE_OPERATORS:
                self._operator(char, 1)
            elif char in PUNCTUATION:
                self._emit("PUNCT", char, char, 1)
            else:
                start = self._position()
                bad = self._advance()
                span = self._span(start)
                self.diagnostics.append(
                    Diagnostic(
                        "LEX_INVALID_CHAR",
                        "lexical",
                        "error",
                        f"Carácter no permitido: {bad!r}",
                        span,
                        "Elimine el carácter o sustitúyalo por un símbolo de la gramática.",
                    )
                )
        eof = self._position()
        self.tokens.append(Token("EOF", "", None, self._span(eof)))
        return LexResult(self.tokens, self.diagnostics)

    def _peek(self, distance: int = 0) -> str:
        index = self.offset + distance
        return self.source[index] if index < self.length else ""

    def _position(self) -> tuple[int, int, int]:
        return self.offset, self.line, self.column

    def _span(self, start: tuple[int, int, int]) -> Span:
        start_offset, start_line, start_column = start
        return Span(start_offset, self.offset, start_line, start_column, self.line, self.column)

    def _advance(self) -> str:
        char = self.source[self.offset]
        self.offset += 1
        self.column += 1
        return char

    def _emit(self, kind: str, lexeme: str, value: str | float | bool | None, width: int) -> None:
        start = self._position()
        self.offset += width
        self.column += width
        self.tokens.append(Token(kind, lexeme, value, self._span(start)))

    def _newline(self) -> None:
        start = self._position()
        if self.source.startswith("\r\n", self.offset):
            self.offset += 2
        else:
            self.offset += 1
        self.tokens.append(
            Token("NEWLINE", "\n", None, Span(start[0], self.offset, start[1], start[2], self.line + 1, 1))
        )
        self.line += 1
        self.column = 1

    def _comment(self) -> None:
        while self.offset < self.length and self.source[self.offset] not in "\r\n":
            self._advance()

    @staticmethod
    def _is_identifier_start(char: str) -> bool:
        return char == "_" or unicodedata.category(char).startswith("L")

    @staticmethod
    def _is_identifier_continue(char: str) -> bool:
        category = unicodedata.category(char)
        return char == "_" or category.startswith(("L", "M", "N"))

    def _identifier(self) -> None:
        start = self._position()
        begin = self.offset
        self._advance()
        while self.offset < self.length and self._is_identifier_continue(self.source[self.offset]):
            self._advance()
        lexeme = self.source[begin : self.offset]
        normalized = unicodedata.normalize("NFC", lexeme)
        folded = normalized.casefold()
        if folded == "modulo":
            self.tokens.append(Token("OP", lexeme, "%", self._span(start)))
        elif folded in {"verdadero", "falso"}:
            self.tokens.append(Token("BOOL", lexeme, folded == "verdadero", self._span(start)))
        elif folded in KEYWORDS:
            self.tokens.append(Token("KEYWORD", lexeme, folded, self._span(start)))
        else:
            self.tokens.append(Token("IDENT", lexeme, normalized, self._span(start)))

    def _number(self) -> None:
        start = self._position()
        begin = self.offset
        if self._peek() == ".":
            self._advance()
            while (
                self.offset < self.length and self.source[self.offset].isascii() and self.source[self.offset].isdigit()
            ):
                self._advance()
        else:
            while (
                self.offset < self.length and self.source[self.offset].isascii() and self.source[self.offset].isdigit()
            ):
                self._advance()
            if self._peek() == "." and self._peek(1).isascii() and self._peek(1).isdigit():
                self._advance()
                while (
                    self.offset < self.length
                    and self.source[self.offset].isascii()
                    and self.source[self.offset].isdigit()
                ):
                    self._advance()
        lexeme = self.source[begin : self.offset]
        try:
            value = float(lexeme)
        except ValueError:
            value = math.inf
        if not math.isfinite(value):
            self.diagnostics.append(
                Diagnostic(
                    "LEX_INVALID_NUMBER", "lexical", "error", "El literal numérico no es finito.", self._span(start)
                )
            )
        self.tokens.append(Token("NUMBER", lexeme, value, self._span(start)))

    def _string(self) -> None:
        start = self._position()
        self._advance()  # opening quote
        value: list[str] = []
        closed = False
        while self.offset < self.length:
            char = self.source[self.offset]
            if char == '"':
                self._advance()
                closed = True
                break
            if char in "\r\n":
                break
            if char == "\\":
                escape_start = self._position()
                self._advance()
                escaped = self._peek()
                mapping = {"\\": "\\", '"': '"', "n": "\n", "t": "\t"}
                if escaped in mapping:
                    self._advance()
                    value.append(mapping[escaped])
                else:
                    if escaped:
                        self._advance()
                    self.diagnostics.append(
                        Diagnostic(
                            "LEX_INVALID_ESCAPE",
                            "lexical",
                            "error",
                            f"Escape inválido: \\{escaped}",
                            self._span(escape_start),
                            "Use barra invertida, comilla doble, salto de línea o tabulación.",
                        )
                    )
                    if escaped:
                        value.append(escaped)
                continue
            value.append(self._advance())
        lexeme = self.source[start[0] : self.offset]
        if not closed:
            self.diagnostics.append(
                Diagnostic(
                    "LEX_UNTERMINATED_STRING",
                    "lexical",
                    "error",
                    "Cadena sin comilla de cierre.",
                    self._span(start),
                    "Cierre el literal con una comilla doble en la misma línea.",
                )
            )
        self.tokens.append(Token("STRING", lexeme, "".join(value), self._span(start)))

    def _operator(self, operator: str, width: int) -> None:
        self._emit("OP", operator, operator, width)


def lex(source: str) -> LexResult:
    return Lexer(source).scan()
