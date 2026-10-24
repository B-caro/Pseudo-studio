"""Recursive-descent statement parser and Pratt expression parser."""

from __future__ import annotations

from dataclasses import dataclass

from .model import (
    Assign,
    Binary,
    Call,
    Diagnostic,
    Dimension,
    ExprStatement,
    For,
    Function,
    If,
    Index,
    Literal,
    Name,
    Program,
    Read,
    Return,
    Span,
    Statement,
    Token,
    Unary,
    While,
    Write,
)


@dataclass(slots=True)
class ParseResult:
    program: Program | None
    diagnostics: list[Diagnostic]


class ParseFailure(Exception):
    pass


PRECEDENCE = {
    "o": 1,
    "y": 2,
    "==": 3,
    "!=": 3,
    ">": 4,
    "<": 4,
    ">=": 4,
    "<=": 4,
    "+": 5,
    "-": 5,
    "*": 6,
    "/": 6,
    "%": 6,
}


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0
        self.diagnostics: list[Diagnostic] = []

    def parse(self) -> ParseResult:
        program: Program | None = None
        try:
            start = self._expect_keyword("inicio", "El programa debe comenzar con Inicio.")
            self._line_end("El encabezado Inicio debe terminar en una línea nueva.")
            body = self._parse_block({"fin"})
            end = self._expect_keyword("fin", "Falta Fin para cerrar el programa.")
            end_span = end.span
            if self._match_kind("NEWLINE"):
                end_span = self._previous().span
                while self._match_kind("NEWLINE"):
                    end_span = self._previous().span
            self._expect_kind("EOF", "Hay contenido después de Fin.")
            program = Program(
                node_id=self._id("Program", start.span, end_span), span=self._join(start.span, end_span), body=body
            )
        except ParseFailure:
            self._synchronize()
        return ParseResult(program, self.diagnostics)

    def _parse_block(self, terminators: set[str]) -> list[Statement]:
        statements: list[Statement] = []
        self._skip_newlines()
        while not self._at("EOF"):
            if self._is_keyword_in(terminators):
                break
            # `Fin` before the current terminator is left for the caller to diagnose.
            if self._is_keyword("fin"):
                break
            previous = self.index
            try:
                statements.append(self._statement())
            except ParseFailure:
                self._synchronize()
            self._skip_newlines()
            if self.index == previous:
                self._advance()
        return statements

    def _statement(self) -> Statement:
        if self._is_keyword("leer") or self._is_keyword("leertexto"):
            return self._read()
        if self._is_keyword("escribir"):
            return self._write()
        if self._is_keyword("si"):
            return self._if()
        if self._is_keyword("para"):
            return self._for()
        if self._is_keyword("mientras"):
            return self._while()
        if self._is_keyword("dimension"):
            return self._dimension()
        if self._is_keyword("retornar"):
            return self._return()
        if self._is_keyword("funcion"):
            return self._function()
        if self._check_kind("IDENT"):
            return self._assignment_or_call()
        token = self._current()
        self._fail("SYN_UNEXPECTED_TOKEN", f"No se esperaba {token.lexeme or 'fin de archivo'}.", token.span)

    def _read(self) -> Read:
        keyword = self._advance()
        target = self._target()
        end = self._line_end("Leer debe terminar al final de línea.")
        return Read(
            node_id=self._id("Read", keyword.span, end.span),
            span=self._join(keyword.span, end.span),
            target=target,
            text=keyword.value == "leertexto",
        )

    def _write(self) -> Write:
        start = self._advance()
        values = [self._expression()]
        while self._match_lexeme(","):
            values.append(self._expression())
        end = self._line_end("Escribir debe terminar al final de línea.")
        return Write(
            node_id=self._id("Write", start.span, end.span), span=self._join(start.span, end.span), values=values
        )

    def _if(self) -> If:
        start = self._advance()
        condition = self._expression()
        self._expect_keyword("entonces", "La condición Si debe terminar con Entonces.")
        self._line_end("Entonces debe terminar al final de línea.")
        then_body = self._parse_block({"sino", "finsi"})
        else_body: list[Statement] = []
        if self._match_keyword("sino"):
            self._line_end("Sino debe terminar al final de línea.")
            else_body = self._parse_block({"finsi"})
        self._expect_keyword("finsi", "Falta FinSi para cerrar Si.")
        end_line = self._line_end("FinSi debe terminar al final de línea.")
        return If(
            node_id=self._id("If", start.span, end_line.span),
            span=self._join(start.span, end_line.span),
            condition=condition,
            then_body=then_body,
            else_body=else_body,
        )

    def _for(self) -> For:
        start = self._advance()
        variable = self._expect_kind("IDENT", "Para requiere un identificador de control.")
        self._expect_lexeme("=", "Falta '=' después del identificador de Para.")
        initial = self._expression()
        self._expect_keyword("hasta", "Falta Hasta en el encabezado Para.")
        end_value = self._expression()
        step = self._expression() if self._match_keyword("paso") else None
        self._expect_keyword("hacer", "Falta Hacer en el encabezado Para.")
        self._line_end("Hacer debe terminar al final de línea.")
        body = self._parse_block({"finpara"})
        self._expect_keyword("finpara", "Falta FinPara para cerrar Para.")
        end_line = self._line_end("FinPara debe terminar al final de línea.")
        name = str(variable.value)
        return For(
            node_id=self._id("For", start.span, end_line.span),
            span=self._join(start.span, end_line.span),
            variable=variable.lexeme,
            normalized_variable=name,
            start=initial,
            end=end_value,
            step=step,
            body=body,
        )

    def _while(self) -> While:
        start = self._advance()
        condition = self._expression()
        self._expect_keyword("hacer", "Falta Hacer en el encabezado Mientras.")
        self._line_end("Hacer debe terminar al final de línea.")
        body = self._parse_block({"finmientras"})
        self._expect_keyword("finmientras", "Falta FinMientras para cerrar Mientras.")
        end = self._line_end("FinMientras debe terminar al final de línea.")
        return While(
            node_id=self._id("While", start.span, end.span),
            span=self._join(start.span, end.span),
            condition=condition,
            body=body,
        )

    def _dimension(self) -> Dimension:
        start = self._advance()
        name = self._expect_kind("IDENT", "Dimension requiere un nombre de arreglo.")
        self._expect_lexeme("[", "Falta '[' después del nombre de arreglo.")
        size = self._expression()
        self._expect_lexeme("]", "Falta ']' después del tamaño de arreglo.")
        end = self._line_end("Dimension debe terminar al final de línea.")
        return Dimension(
            node_id=self._id("Dimension", start.span, end.span),
            span=self._join(start.span, end.span),
            name=name.lexeme,
            normalized_name=str(name.value),
            size=size,
        )

    def _return(self) -> Return:
        start = self._advance()
        value = self._expression()
        end = self._line_end("Retornar debe terminar al final de línea.")
        return Return(
            node_id=self._id("Return", start.span, end.span), span=self._join(start.span, end.span), value=value
        )

    def _function(self) -> Function:
        start = self._advance()
        first = self._expect_kind("IDENT", "Funcion requiere un nombre.")
        alias: Token | None = None
        if self._match_lexeme("="):
            alias = first
            name = self._expect_kind("IDENT", "Falta el nombre de función después del alias.")
        else:
            name = first
        self._expect_lexeme("(", "Falta '(' en la declaración de función.")
        parameters: list[Token] = []
        if not self._check_lexeme(")"):
            parameters.append(self._expect_kind("IDENT", "El parámetro debe ser un identificador."))
            while self._match_lexeme(","):
                parameters.append(self._expect_kind("IDENT", "El parámetro debe ser un identificador."))
        self._expect_lexeme(")", "Falta ')' en la declaración de función.")
        self._line_end("El encabezado Funcion debe terminar al final de línea.")
        body = self._parse_block({"finfuncion"})
        self._expect_keyword("finfuncion", "Falta FinFuncion para cerrar Funcion.")
        end = self._line_end("FinFuncion debe terminar al final de línea.")
        return Function(
            node_id=self._id("Function", start.span, end.span),
            span=self._join(start.span, end.span),
            name=name.lexeme,
            normalized_name=str(name.value),
            return_alias=alias.lexeme if alias else None,
            normalized_return_alias=str(alias.value) if alias else None,
            parameters=[token.lexeme for token in parameters],
            normalized_parameters=[str(token.value) for token in parameters],
            body=body,
        )

    def _assignment_or_call(self) -> Statement:
        start = self._current()
        target = self._target()
        if self._match_lexeme("="):
            value = self._expression()
            end = self._line_end("La asignación debe terminar al final de línea.")
            return Assign(
                node_id=self._id("Assign", start.span, end.span),
                span=self._join(start.span, end.span),
                target=target,
                value=value,
            )
        if isinstance(target, Name) and self._check_lexeme("("):
            expression = self._call(str(target.identifier), target.span)
            end = self._line_end("La llamada debe terminar al final de línea.")
            return ExprStatement(
                node_id=self._id("ExprStatement", start.span, end.span),
                span=self._join(start.span, end.span),
                expression=expression,
            )
        self._fail("SYN_EXPECTED_ASSIGNMENT", "Se esperaba '=' o una llamada a función.", self._current().span)

    def _target(self) -> Name | Index:
        token = self._expect_kind("IDENT", "Se esperaba un identificador.")
        name = Name(
            node_id=self._id("Name", token.span, token.span),
            span=token.span,
            identifier=token.lexeme,
            normalized=str(token.value),
        )
        if self._match_lexeme("["):
            index = self._expression()
            closing = self._expect_lexeme("]", "Falta ']' en el acceso indexado.")
            return Index(
                node_id=self._id("Index", token.span, closing.span),
                span=self._join(token.span, closing.span),
                array=name,
                index=index,
            )
        return name

    def _expression(self, min_precedence: int = 1):
        left = self._prefix()
        while True:
            token = self._current()
            operator = self._operator_value(token)
            precedence = PRECEDENCE.get(operator or "", 0)
            if precedence < min_precedence:
                break
            self._advance()
            right = self._expression(precedence + 1)
            left = Binary(
                node_id=self._id("Binary", left.span, right.span),
                span=self._join(left.span, right.span),
                left=left,
                operator=operator,
                right=right,
            )
        return left

    def _prefix(self):
        token = self._current()
        operator = self._operator_value(token)
        if operator in {"-", "+", "no"}:
            self._advance()
            operand = self._expression(7)
            return Unary(
                node_id=self._id("Unary", token.span, operand.span),
                span=self._join(token.span, operand.span),
                operator=operator,
                operand=operand,
            )
        return self._primary()

    def _primary(self):
        token = self._current()
        if self._match_kind("NUMBER"):
            return Literal(
                node_id=self._id("Literal", token.span, token.span),
                span=token.span,
                value=float(token.value),
                literal_kind="number",
            )
        if self._match_kind("STRING"):
            return Literal(
                node_id=self._id("Literal", token.span, token.span),
                span=token.span,
                value=str(token.value),
                literal_kind="string",
            )
        if self._match_kind("BOOL"):
            return Literal(
                node_id=self._id("Literal", token.span, token.span),
                span=token.span,
                value=bool(token.value),
                literal_kind="boolean",
            )
        if self._match_lexeme("("):
            expression = self._expression()
            self._expect_lexeme(")", "Falta ')' para cerrar la expresión.")
            return expression
        if self._match_kind("IDENT"):
            if self._check_lexeme("("):
                return self._call(str(token.value), token.span)
            name = Name(
                node_id=self._id("Name", token.span, token.span),
                span=token.span,
                identifier=token.lexeme,
                normalized=str(token.value),
            )
            if self._match_lexeme("["):
                index = self._expression()
                closing = self._expect_lexeme("]", "Falta ']' en el acceso indexado.")
                return Index(
                    node_id=self._id("Index", token.span, closing.span),
                    span=self._join(token.span, closing.span),
                    array=name,
                    index=index,
                )
            return name
        self._fail("SYN_EXPECTED_EXPRESSION", "Se esperaba una expresión.", token.span)

    def _call(self, function: str, start_span: Span) -> Call:
        self._expect_lexeme("(", "Falta '(' en la llamada.")
        arguments = []
        if not self._check_lexeme(")"):
            arguments.append(self._expression())
            while self._match_lexeme(","):
                arguments.append(self._expression())
        end = self._expect_lexeme(")", "Falta ')' en la llamada.")
        return Call(
            node_id=self._id("Call", start_span, end.span),
            span=self._join(start_span, end.span),
            function=function,
            arguments=arguments,
        )

    def _line_end(self, message: str) -> Token:
        if self._match_kind("NEWLINE"):
            return self._previous()
        if self._check_kind("EOF") and self._is_keyword("fin"):
            return self._current()
        self._fail("SYN_EXPECTED_NEWLINE", message, self._current().span)

    def _operator_value(self, token: Token) -> str | None:
        if token.kind == "OP":
            return str(token.value)
        if token.kind == "KEYWORD" and token.value in {"y", "o", "no"}:
            return str(token.value)
        return None

    def _synchronize(self) -> None:
        if not self._check_kind("EOF") and not self._check_kind("NEWLINE"):
            self._advance()
        while not self._check_kind("EOF"):
            if self._previous().kind == "NEWLINE":
                return
            if self._check_kind("NEWLINE"):
                self._advance()
                return
            if self._is_keyword_in({"sino", "finsi", "finpara", "finmientras", "finfuncion", "fin"}):
                return
            self._advance()

    def _fail(self, code: str, message: str, span: Span) -> None:
        self.diagnostics.append(Diagnostic(code, "syntax", "error", message, span, self._syntax_hint(code, message)))
        raise ParseFailure

    @staticmethod
    def _syntax_hint(code: str, message: str) -> str:
        if "Falta " in message:
            expected = message.split("Falta ", 1)[1].split(" ", 1)[0].rstrip(".,")
            return f"Agregue {expected} para cerrar o completar el bloque indicado."
        if "Inicio" in message and "comenzar" in message:
            return "Coloque Inicio en la primera línea del programa."
        if "Hasta" in message:
            return "Escriba Hasta seguido de la expresión que fija el límite del ciclo Para."
        if "Entonces" in message:
            return "Escriba Entonces después de la condición de Si."
        if "Hacer" in message:
            return "Escriba Hacer al final del encabezado del ciclo."
        if "identificador" in message and "Para" in message:
            return "Escriba el nombre de la variable de control después de Para."
        if "Se esperaba '='" in message:
            return "Coloque = entre el identificador y la expresión, o convierta la línea en una llamada válida."
        if "expresión" in message:
            return "Agregue un número, cadena, booleano, variable, llamada o expresión entre paréntesis."
        if "línea nueva" in message or "al final de línea" in message:
            return "Coloque la siguiente sentencia en una línea nueva."
        if code == "SYN_EXPECTED_ASSIGNMENT":
            return "Use la forma nombre = expresión o escriba una llamada válida a función."
        if code == "SYN_EXPECTED_NEWLINE":
            return "Termine la sentencia y coloque cada instrucción en una línea separada."
        return "Revise el elemento señalado y complete o cierre la construcción que está escribiendo."

    def _expect_keyword(self, keyword: str, message: str) -> Token:
        if self._is_keyword(keyword):
            return self._advance()
        self._fail("SYN_UNEXPECTED_TOKEN", message, self._current().span)

    def _expect_kind(self, kind: str, message: str) -> Token:
        if self._check_kind(kind):
            return self._advance()
        self._fail("SYN_UNEXPECTED_TOKEN", message, self._current().span)

    def _expect_lexeme(self, lexeme: str, message: str) -> Token:
        if self._check_lexeme(lexeme):
            return self._advance()
        self._fail("SYN_UNEXPECTED_TOKEN", message, self._current().span)

    def _line_end_or_eof(self) -> bool:
        return self._check_kind("NEWLINE") or self._check_kind("EOF")

    def _is_keyword(self, keyword: str) -> bool:
        token = self._current()
        return token.kind == "KEYWORD" and token.value == keyword

    def _is_keyword_in(self, keywords: set[str]) -> bool:
        token = self._current()
        return token.kind == "KEYWORD" and token.value in keywords

    def _match_keyword(self, keyword: str) -> bool:
        if self._is_keyword(keyword):
            self._advance()
            return True
        return False

    def _match_lexeme(self, lexeme: str) -> bool:
        if self._check_lexeme(lexeme):
            self._advance()
            return True
        return False

    def _match_kind(self, kind: str) -> bool:
        if self._check_kind(kind):
            self._advance()
            return True
        return False

    def _check_kind(self, kind: str) -> bool:
        return self._current().kind == kind

    def _check_lexeme(self, lexeme: str) -> bool:
        return self._current().lexeme == lexeme

    def _at(self, kind: str) -> bool:
        return self._check_kind(kind)

    def _current(self) -> Token:
        return self.tokens[min(self.index, len(self.tokens) - 1)]

    def _previous(self) -> Token:
        return self.tokens[max(0, self.index - 1)]

    def _advance(self) -> Token:
        current = self._current()
        if current.kind != "EOF":
            self.index += 1
        return current

    def _skip_newlines(self) -> None:
        while self._match_kind("NEWLINE"):
            pass

    @staticmethod
    def _join(start: Span, end: Span) -> Span:
        return Span(start.start, end.end, start.start_line, start.start_column, end.end_line, end.end_column)

    @staticmethod
    def _id(kind: str, start: Span, end: Span) -> str:
        return f"{kind.lower()}:{start.start}:{end.end}"


def parse(tokens: list[Token]) -> ParseResult:
    return Parser(tokens).parse()
