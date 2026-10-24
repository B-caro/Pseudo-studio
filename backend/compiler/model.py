"""Typed source model shared by the lexer, parser, analyzer, and generators."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any, TypeAlias

DIAGNOSTIC_HINTS = {
    "LEX_INVALID_CHAR": "Elimine este carácter o reemplácelo por un operador o signo admitido por la gramática.",
    "LEX_INVALID_NUMBER": "Use un número decimal finito con dígitos ASCII y, como máximo, un punto decimal.",
    "LEX_INVALID_ESCAPE": "Dentro de cadenas use solo las secuencias de escape documentadas por el lenguaje.",
    "LEX_UNTERMINATED_STRING": "Cierre la cadena con una comilla doble en la misma línea.",
    "SYN_UNEXPECTED_TOKEN": "Revise el elemento señalado y complete o cierre la construcción que está escribiendo.",
    "SYN_EXPECTED_ASSIGNMENT": "Use la forma nombre = expresión o escriba una llamada válida a función.",
    "SYN_EXPECTED_EXPRESSION": "Agregue un valor, nombre, llamada, expresión entre paréntesis o valor lógico.",
    "SYN_EXPECTED_NEWLINE": "Termine la sentencia y coloque cada instrucción en una línea separada.",
    "SEM_DUPLICATE_FUNCTION": "Cambie el nombre o conserve una sola definición de la función.",
    "SEM_INVALID_STEP": "Use un paso distinto de cero y con la dirección deseada para el límite.",
    "SEM_INVALID_DIMENSION": "Dimension requiere una expresión que produzca un entero positivo y seguro.",
    "SEM_TYPE_MISMATCH": "Haga coincidir el tipo con el uso esperado; número, texto, booleano y arreglo no son intercambiables.",
    "SEM_RETURN_OUTSIDE_FUNCTION": "Mueva Retornar dentro de una función y devuelva un valor compatible con sus llamadas.",
    "SEM_ASSIGN_FUNCTION": "Use el nombre de la función en una llamada; no se puede reutilizar para una variable.",
    "SEM_UNDEFINED_IDENTIFIER": "Declare o asigne la variable antes de leerla, o compruebe la escritura de su nombre.",
    "SEM_EXPECTED_VALUE": "Llame la función con paréntesis y los argumentos requeridos.",
    "SEM_UNINITIALIZED": "Asigne un valor a la variable o a la posición del arreglo antes de leerla.",
    "SEM_DIV_ZERO": "Cambie el divisor constante por un valor distinto de cero.",
    "SEM_UNDEFINED_FUNCTION": "Defina la función antes de usarla y compruebe su nombre.",
    "SEM_WRONG_ARITY": "Pase la cantidad de argumentos que declara la función.",
}


@dataclass(frozen=True, slots=True)
class Span:
    start: int
    end: int
    start_line: int
    start_column: int
    end_line: int
    end_column: int

    def to_dict(self) -> dict[str, int]:
        return {
            "start": self.start,
            "end": self.end,
            "start_line": self.start_line,
            "start_column": self.start_column,
            "end_line": self.end_line,
            "end_column": self.end_column,
        }


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    stage: str
    severity: str
    message: str
    span: Span
    hint: str | None = None

    def __post_init__(self) -> None:
        if self.hint is None:
            object.__setattr__(self, "hint", DIAGNOSTIC_HINTS.get(self.code))

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "stage": self.stage,
            "severity": self.severity,
            "message": self.message,
            "span": self.span.to_dict(),
            "hint": self.hint,
        }


@dataclass(frozen=True, slots=True)
class Token:
    kind: str
    lexeme: str
    value: str | float | bool | None
    span: Span

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "lexeme": self.lexeme,
            "value": self.value,
            "span": self.span.to_dict(),
        }


@dataclass(slots=True, kw_only=True)
class Node:
    node_id: str
    span: Span
    inferred_type: str | None = None


@dataclass(slots=True, kw_only=True)
class Program(Node):
    body: list[Statement]


@dataclass(slots=True, kw_only=True)
class Literal(Node):
    value: float | bool | str
    literal_kind: str


@dataclass(slots=True, kw_only=True)
class Name(Node):
    identifier: str
    normalized: str


@dataclass(slots=True, kw_only=True)
class Unary(Node):
    operator: str
    operand: Expression


@dataclass(slots=True, kw_only=True)
class Binary(Node):
    left: Expression
    operator: str
    right: Expression


@dataclass(slots=True, kw_only=True)
class Call(Node):
    function: str
    arguments: list[Expression]


@dataclass(slots=True, kw_only=True)
class Index(Node):
    array: Expression
    index: Expression


@dataclass(slots=True, kw_only=True)
class Assign(Node):
    target: Name | Index
    value: Expression


@dataclass(slots=True, kw_only=True)
class Read(Node):
    target: Name | Index
    text: bool = False


@dataclass(slots=True, kw_only=True)
class Write(Node):
    values: list[Expression]


@dataclass(slots=True, kw_only=True)
class If(Node):
    condition: Expression
    then_body: list[Statement]
    else_body: list[Statement]


@dataclass(slots=True, kw_only=True)
class For(Node):
    variable: str
    normalized_variable: str
    start: Expression
    end: Expression
    step: Expression | None
    body: list[Statement]


@dataclass(slots=True, kw_only=True)
class While(Node):
    condition: Expression
    body: list[Statement]


@dataclass(slots=True, kw_only=True)
class Dimension(Node):
    name: str
    normalized_name: str
    size: Expression


@dataclass(slots=True, kw_only=True)
class Return(Node):
    value: Expression


@dataclass(slots=True, kw_only=True)
class ExprStatement(Node):
    expression: Call


@dataclass(slots=True, kw_only=True)
class Function(Node):
    name: str
    normalized_name: str
    return_alias: str | None
    normalized_return_alias: str | None
    parameters: list[str]
    normalized_parameters: list[str]
    body: list[Statement]


Expression: TypeAlias = Literal | Name | Unary | Binary | Call | Index
Statement: TypeAlias = Assign | Read | Write | If | For | While | Dimension | Return | ExprStatement | Function


def serialize(value: Any) -> Any:
    """Convert compiler data into JSON-safe values without serializing runtime objects."""
    if isinstance(value, Span):
        return value.to_dict()
    if isinstance(value, (Diagnostic, Token)):
        return value.to_dict()
    if is_dataclass(value):
        result: dict[str, Any] = {"kind": type(value).__name__}
        for field in fields(value):
            result[field.name] = serialize(getattr(value, field.name))
        return result
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if isinstance(value, tuple):
        return [serialize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serialize(item) for key, item in value.items()}
    return value
