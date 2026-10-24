"""Static type, scope, initialization, function, and array analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .model import (
    Assign,
    Binary,
    Call,
    Diagnostic,
    Dimension,
    Expression,
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
    Unary,
    While,
    Write,
)

UNKNOWN = "unknown"


@dataclass(slots=True)
class Symbol:
    name: str
    scope: str
    kind: str
    type: str
    declaration_span: Span
    initialized: bool = False
    display_name: str | None = None
    references: list[Span] = field(default_factory=list)
    reads: int = 0
    writes: int = 0
    element_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.display_name or self.name,
            "normalized_name": self.name,
            "scope": self.scope,
            "kind": self.kind,
            "type": self.type,
            "declaration_span": self.declaration_span.to_dict(),
            "initialized": self.initialized,
            "references": [span.to_dict() for span in self.references],
            "reads": self.reads,
            "writes": self.writes,
            "element_type": self.element_type,
        }


@dataclass(slots=True)
class FunctionInfo:
    node: Function
    scope: str
    return_type: str = UNKNOWN
    global_reads: set[str] = field(default_factory=set)
    called_functions: set[str] = field(default_factory=set)
    has_value_return: bool = False
    return_types: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SemanticResult:
    symbols: list[Symbol]
    diagnostics: list[Diagnostic]
    function_info: dict[str, FunctionInfo]


class SemanticAnalyzer:
    def __init__(self, program: Program) -> None:
        self.program = program
        self.diagnostics: list[Diagnostic] = []
        self.symbols: dict[tuple[str, str], Symbol] = {}
        self.function_info: dict[str, FunctionInfo] = {}
        self.scope = "global"
        self.current_function: FunctionInfo | None = None
        self.initialized: dict[tuple[str, str], bool] = {}
        self.inside_function = False

    def analyze(self) -> SemanticResult:
        functions = [stmt for stmt in self.program.body if isinstance(stmt, Function)]
        for function in functions:
            if function.normalized_name in self.function_info:
                self._diag(
                    "SEM_DUPLICATE_FUNCTION",
                    f"La función '{function.name}' está definida más de una vez.",
                    function.span,
                )
                continue
            scope = f"function:{function.normalized_name}"
            info = FunctionInfo(function, scope)
            self.function_info[function.normalized_name] = info
            self._declare(function.normalized_name, "global", "function", UNKNOWN, function.span, True, function.name)

        self._predeclare_globals([stmt for stmt in self.program.body if not isinstance(stmt, Function)])
        for info in self.function_info.values():
            self._analyze_function(info)
        self._check_function_global_reads()
        for statement in self.program.body:
            if not isinstance(statement, Function):
                self._statement(statement)
        for symbol in self.symbols.values():
            symbol.initialized = self.initialized.get((symbol.scope, symbol.name), symbol.initialized)
        return SemanticResult(list(self.symbols.values()), self.diagnostics, self.function_info)

    def _predeclare_globals(self, statements: list[Statement]) -> None:
        for statement in statements:
            for name, span, kind in self._declared_names(statement):
                key = ("global", name)
                if key not in self.symbols:
                    self._declare(name, "global", kind, UNKNOWN, span, False, name)

    def _declared_names(self, statement: Statement):
        if isinstance(statement, Assign) and isinstance(statement.target, Name):
            yield statement.target.normalized, statement.target.span, "variable"
        elif isinstance(statement, Read) and isinstance(statement.target, Name):
            yield statement.target.normalized, statement.target.span, "variable"
        elif isinstance(statement, Dimension):
            yield statement.normalized_name, statement.span, "array"
        elif isinstance(statement, For):
            yield statement.normalized_variable, statement.span, "variable"
            for child in statement.body:
                yield from self._declared_names(child)
        elif isinstance(statement, If):
            for child in statement.then_body + statement.else_body:
                yield from self._declared_names(child)
        elif isinstance(statement, While):
            for child in statement.body:
                yield from self._declared_names(child)

    def _analyze_function(self, info: FunctionInfo) -> None:
        previous_scope = self.scope
        previous_function = self.current_function
        previous_inside = self.inside_function
        previous_initialized = self.initialized
        self.scope = info.scope
        self.current_function = info
        self.inside_function = True
        self.initialized = {}
        function = info.node
        local_declarations: dict[str, tuple[str, Span]] = {}
        for parameter, span in zip(
            function.normalized_parameters, [function.span] * len(function.parameters), strict=True
        ):
            local_declarations[parameter] = ("parameter", span)
        if function.normalized_return_alias:
            local_declarations[function.normalized_return_alias] = ("variable", function.span)
        for child in function.body:
            for name, span, kind in self._declared_names(child):
                local_declarations.setdefault(name, (kind, span))
        for name, (kind, span) in local_declarations.items():
            initialized = kind == "parameter"
            self._declare(name, self.scope, kind, UNKNOWN, span, initialized, name)
        for child in function.body:
            self._statement(child)
        if info.return_types:
            info.has_value_return = True
            info.return_type = self._join_types(info.return_types)
        self.scope = previous_scope
        self.current_function = previous_function
        self.inside_function = previous_inside
        self.initialized = previous_initialized

    def _statement(self, statement: Statement) -> None:
        if isinstance(statement, Function):
            return
        if isinstance(statement, Assign):
            value_type = self._expression(statement.value)
            self._assign(statement.target, value_type, statement.span)
            return
        if isinstance(statement, Read):
            value_type = "string" if statement.text else "number"
            self._assign(statement.target, value_type, statement.span)
            return
        if isinstance(statement, Write):
            for value in statement.values:
                self._expression(value)
            return
        if isinstance(statement, If):
            condition_type = self._expression(statement.condition)
            self._require_type(
                condition_type, "boolean", statement.condition.span, "La condición Si debe ser booleana."
            )
            before = self.initialized.copy()
            self._analyze_statements(statement.then_body)
            then_state = self.initialized.copy()
            self.initialized = before.copy()
            self._analyze_statements(statement.else_body)
            else_state = self.initialized.copy()
            self.initialized = {
                key: then_state.get(key, False) and else_state.get(key, False)
                for key in set(before) | set(then_state) | set(else_state)
            }
            return
        if isinstance(statement, For):
            start_type = self._expression(statement.start)
            end_type = self._expression(statement.end)
            self._require_type(start_type, "number", statement.start.span, "El inicio de Para debe ser numérico.")
            self._require_type(end_type, "number", statement.end.span, "El límite de Para debe ser numérico.")
            step_type = self._expression(statement.step) if statement.step else "number"
            if statement.step:
                self._require_type(step_type, "number", statement.step.span, "Paso debe ser numérico.")
                constant_step = self._constant_number(statement.step)
                if constant_step == 0:
                    self._diag("SEM_INVALID_STEP", "Paso no puede ser cero.", statement.step.span)
            variable = self._resolve(statement.normalized_variable)
            if variable is None:
                variable = self._declare(
                    statement.normalized_variable,
                    self.scope,
                    "variable",
                    "number",
                    statement.span,
                    True,
                    statement.variable,
                )
            else:
                self._constrain_symbol(variable, "number", statement.span)
            self._write_symbol(variable, statement.span)
            before = self.initialized.copy()
            self.initialized[(variable.scope, variable.name)] = True
            self._analyze_statements(statement.body)
            body_state = self.initialized.copy()
            self.initialized = {
                key: before.get(key, False) and body_state.get(key, False) for key in set(before) | set(body_state)
            }
            self.initialized[(variable.scope, variable.name)] = True
            return
        if isinstance(statement, While):
            condition_type = self._expression(statement.condition)
            self._require_type(
                condition_type, "boolean", statement.condition.span, "La condición Mientras debe ser booleana."
            )
            before = self.initialized.copy()
            self._analyze_statements(statement.body)
            body_state = self.initialized.copy()
            self.initialized = {
                key: before.get(key, False) and body_state.get(key, False) for key in set(before) | set(body_state)
            }
            return
        if isinstance(statement, Dimension):
            size_type = self._expression(statement.size)
            self._require_type(size_type, "number", statement.size.span, "El tamaño de Dimension debe ser numérico.")
            constant = self._constant_number(statement.size)
            if constant is not None and (constant <= 0 or not constant.is_integer() or constant > 2**53 - 1):
                self._diag(
                    "SEM_INVALID_DIMENSION",
                    "El tamaño del arreglo debe ser un entero positivo y seguro.",
                    statement.size.span,
                )
            symbol = self._resolve(statement.normalized_name)
            if symbol is None:
                symbol = self._declare(
                    statement.normalized_name, self.scope, "array", "array", statement.span, True, statement.name
                )
            elif symbol.kind != "array":
                self._diag(
                    "SEM_TYPE_MISMATCH", f"'{statement.name}' ya fue declarado como {symbol.kind}.", statement.span
                )
            symbol.kind = "array"
            symbol.type = "array"
            symbol.element_type = symbol.element_type or UNKNOWN
            self._write_symbol(symbol, statement.span)
            self.initialized[(symbol.scope, symbol.name)] = True
            return
        if isinstance(statement, Return):
            value_type = self._expression(statement.value)
            if not self.current_function:
                self._diag(
                    "SEM_RETURN_OUTSIDE_FUNCTION", "Retornar solo puede usarse dentro de una función.", statement.span
                )
            else:
                self.current_function.return_types.append(value_type)
            return
        if isinstance(statement, ExprStatement):
            self._expression(statement.expression)

    def _analyze_statements(self, statements: list[Statement]) -> None:
        for statement in statements:
            self._statement(statement)

    def _assign(self, target: Name | Index, value_type: str, span: Span) -> None:
        if isinstance(target, Name):
            symbol = self._resolve(target.normalized)
            if symbol is None:
                symbol = self._declare(
                    target.normalized, self.scope, "variable", value_type, target.span, True, target.identifier
                )
            elif symbol.kind == "function":
                self._diag(
                    "SEM_ASSIGN_FUNCTION", f"No se puede asignar a la función '{target.identifier}'.", target.span
                )
            else:
                self._constrain_symbol(symbol, value_type, span)
            self._write_symbol(symbol, span)
            self.initialized[(symbol.scope, symbol.name)] = True
            return
        array_type = self._expression(target.array)
        index_type = self._expression(target.index)
        self._require_type(array_type, "array", target.array.span, "El destino indexado debe ser un arreglo.")
        self._require_type(index_type, "number", target.index.span, "El índice debe ser entero.")
        array_symbol = self._resolve(target.array.normalized) if isinstance(target.array, Name) else None
        if array_symbol:
            if array_symbol.element_type in (None, UNKNOWN):
                array_symbol.element_type = value_type
            elif value_type not in (UNKNOWN, array_symbol.element_type):
                self._diag("SEM_TYPE_MISMATCH", "El valor no coincide con el tipo de los elementos del arreglo.", span)
            self._write_symbol(array_symbol, span)

    def _expression(self, expression: Expression | None) -> str:
        if expression is None:
            return UNKNOWN
        if isinstance(expression, Literal):
            result = expression.literal_kind
            expression.inferred_type = result
            return result
        if isinstance(expression, Name):
            symbol = self._resolve(expression.normalized)
            if symbol is None:
                self._diag(
                    "SEM_UNDEFINED_IDENTIFIER", f"Variable '{expression.identifier}' no definida.", expression.span
                )
                return UNKNOWN
            if symbol.kind == "function":
                self._diag(
                    "SEM_EXPECTED_VALUE",
                    f"'{expression.identifier}' es una función y requiere una llamada.",
                    expression.span,
                )
                return UNKNOWN
            self._read_symbol(symbol, expression.span)
            if self.current_function and symbol.scope == "global":
                self.current_function.global_reads.add(symbol.name)
                return symbol.type
            if not self.initialized.get((symbol.scope, symbol.name), symbol.initialized):
                self._diag(
                    "SEM_UNINITIALIZED",
                    f"'{expression.identifier}' puede usarse antes de inicializarse.",
                    expression.span,
                )
            expression.inferred_type = symbol.type
            return symbol.type
        if isinstance(expression, Index):
            array_type = self._expression(expression.array)
            index_type = self._expression(expression.index)
            if array_type == UNKNOWN and isinstance(expression.array, Name):
                symbol = self._resolve(expression.array.normalized)
                if symbol and symbol.kind == "parameter":
                    self._constrain_symbol(symbol, "array", expression.array.span)
                    array_type = "array"
            self._require_type(array_type, "array", expression.array.span, "El acceso indexado requiere un arreglo.")
            self._require_type(index_type, "number", expression.index.span, "El índice debe ser entero.")
            element_type = UNKNOWN
            if isinstance(expression.array, Name):
                symbol = self._resolve(expression.array.normalized)
                if symbol:
                    element_type = symbol.element_type or UNKNOWN
            expression.inferred_type = element_type
            return element_type
        if isinstance(expression, Unary):
            operand = self._expression(expression.operand)
            expected = "boolean" if expression.operator == "no" else "number"
            self._require_type(
                operand, expected, expression.operand.span, "El operador unario no coincide con el tipo del operando."
            )
            expression.inferred_type = expected
            return expected
        if isinstance(expression, Binary):
            left = self._expression(expression.left)
            right = self._expression(expression.right)
            operator = expression.operator
            if operator in {"y", "o"}:
                self._require_type(left, "boolean", expression.left.span, "Y/O requiere operandos booleanos.")
                self._require_type(right, "boolean", expression.right.span, "Y/O requiere operandos booleanos.")
                result = "boolean"
            elif operator in {"==", "!="}:
                self._compatible(left, right, expression.span)
                result = "boolean"
            elif operator in {">", "<", ">=", "<="}:
                self._compatible(left, right, expression.span)
                if left not in (UNKNOWN, "number", "string") or right not in (UNKNOWN, "number", "string"):
                    self._diag(
                        "SEM_TYPE_MISMATCH", "La comparación requiere números o cadenas compatibles.", expression.span
                    )
                result = "boolean"
            elif (
                operator == "+"
                and left in {"string", UNKNOWN}
                and right in {"string", UNKNOWN}
                and "string" in {left, right}
            ):
                if left == UNKNOWN:
                    self._constrain_unknown_name(expression.left, "string", expression.span)
                if right == UNKNOWN:
                    self._constrain_unknown_name(expression.right, "string", expression.span)
                result = "string"
            else:
                self._require_type(left, "number", expression.left.span, "La operación aritmética requiere números.")
                self._require_type(right, "number", expression.right.span, "La operación aritmética requiere números.")
                if operator == "/" and self._constant_number(expression.right) == 0:
                    self._diag("SEM_DIV_ZERO", "División constante entre cero.", expression.right.span)
                result = "number"
            expression.inferred_type = result
            return result
        if isinstance(expression, Call):
            return self._call_expression(expression)
        return UNKNOWN

    def _call_expression(self, expression: Call) -> str:
        info = self.function_info.get(expression.function)
        argument_types = [self._expression(argument) for argument in expression.arguments]
        if info is None:
            self._diag("SEM_UNDEFINED_FUNCTION", f"Función '{expression.function}' no definida.", expression.span)
            return UNKNOWN
        if self.current_function:
            self.current_function.called_functions.add(expression.function)
        else:
            for global_name in info.global_reads:
                symbol = self.symbols.get(("global", global_name))
                if symbol and not self.initialized.get((symbol.scope, symbol.name), symbol.initialized):
                    self._diag(
                        "SEM_UNINITIALIZED",
                        f"La función '{expression.function}' puede leer '{symbol.display_name or symbol.name}' antes de inicializarse.",
                        expression.span,
                    )
        if len(argument_types) != len(info.node.parameters):
            self._diag(
                "SEM_WRONG_ARITY",
                f"'{expression.function}' espera {len(info.node.parameters)} argumentos y recibió {len(argument_types)}.",
                expression.span,
            )
        for argument_type, parameter in zip(argument_types, info.node.normalized_parameters):
            parameter_symbol = self.symbols.get((info.scope, parameter))
            if parameter_symbol:
                self._constrain_symbol(parameter_symbol, argument_type, expression.span)
        expression.inferred_type = info.return_type
        return info.return_type

    def _check_function_global_reads(self) -> None:
        def dependencies(name: str, visited: set[str]) -> set[str]:
            if name in visited:
                return set()
            visited.add(name)
            info = self.function_info.get(name)
            if not info:
                return set()
            result = set(info.global_reads)
            for child in info.called_functions:
                result.update(dependencies(child, visited))
            return result

        for name, info in self.function_info.items():
            info.global_reads.update(dependencies(name, set()))

    def _require_type(self, actual: str, expected: str, span: Span, message: str) -> None:
        if actual not in (UNKNOWN, expected):
            self._diag("SEM_TYPE_MISMATCH", message, span)

    def _compatible(self, left: str, right: str, span: Span) -> None:
        if left != UNKNOWN and right != UNKNOWN and left != right:
            self._diag("SEM_TYPE_MISMATCH", f"Tipos incompatibles: {left} y {right}.", span)

    def _constrain_unknown_name(self, expression: Expression, expected: str, span: Span) -> None:
        if not isinstance(expression, Name):
            return
        symbol = self._resolve(expression.normalized)
        if symbol and symbol.kind != "function":
            self._constrain_symbol(symbol, expected, span)

    def _constrain_symbol(self, symbol: Symbol, expected: str, span: Span) -> None:
        if expected == UNKNOWN:
            return
        if symbol.type == UNKNOWN:
            symbol.type = expected
        elif symbol.type != expected:
            self._diag(
                "SEM_TYPE_MISMATCH", f"'{symbol.name}' tiene tipo {symbol.type}; no puede usarse como {expected}.", span
            )

    def _resolve(self, name: str) -> Symbol | None:
        return self.symbols.get((self.scope, name)) or self.symbols.get(("global", name))

    def _declare(
        self, name: str, scope: str, kind: str, value_type: str, span: Span, initialized: bool, display_name: str
    ) -> Symbol:
        key = (scope, name)
        symbol = self.symbols.get(key)
        if symbol is not None:
            return symbol
        symbol = Symbol(name, scope, kind, value_type, span, initialized, display_name)
        self.symbols[key] = symbol
        self.initialized[key] = initialized
        return symbol

    def _read_symbol(self, symbol: Symbol, span: Span) -> None:
        symbol.references.append(span)
        symbol.reads += 1

    def _write_symbol(self, symbol: Symbol, span: Span) -> None:
        symbol.references.append(span)
        symbol.writes += 1

    def _diag(self, code: str, message: str, span: Span, hint: str | None = None) -> None:
        self.diagnostics.append(Diagnostic(code, "semantic", "error", message, span, hint))

    def _constant_number(self, expression: Expression | None) -> float | None:
        if expression is None:
            return None
        if isinstance(expression, Literal) and expression.literal_kind == "number":
            return float(expression.value)
        if isinstance(expression, Unary) and expression.operator in {"-", "+"}:
            value = self._constant_number(expression.operand)
            return -value if value is not None and expression.operator == "-" else value
        if isinstance(expression, Binary) and expression.operator in {"+", "-", "*", "/", "%"}:
            left = self._constant_number(expression.left)
            right = self._constant_number(expression.right)
            if left is None or right is None:
                return None
            try:
                if expression.operator == "+":
                    return left + right
                if expression.operator == "-":
                    return left - right
                if expression.operator == "*":
                    return left * right
                if right == 0:
                    return None
                if expression.operator == "/":
                    return left / right
                return left - int(left / right) * right
            except (OverflowError, ZeroDivisionError):
                return None
        return None

    @staticmethod
    def _join_types(types: list[str]) -> str:
        non_unknown = {value for value in types if value != UNKNOWN}
        if len(non_unknown) <= 1:
            return next(iter(non_unknown), UNKNOWN)
        return UNKNOWN


def analyze(program: Program) -> SemanticResult:
    return SemanticAnalyzer(program).analyze()
