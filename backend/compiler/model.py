"""Typed source model shared by the lexer, parser, analyzer, and generators."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any, TypeAlias


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
