"""AST-driven emitters for standalone Python 3 and Node.js programs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from backend.compiler.model import (
    Assign,
    Binary,
    Call,
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
from backend.compiler.semantic import Symbol


class GenerationError(ValueError):
    pass


@dataclass(slots=True)
class GeneratedArtifact:
    target: str
    source: str
    artifact_hash: str
    source_map: list[dict[str, object]]
    extension: str

    def to_dict(self) -> dict[str, object]:
        return {
            "target": self.target,
            "source": self.source,
            "artifact_hash": self.artifact_hash,
            "source_map": self.source_map,
            "extension": self.extension,
        }


PY_HELPERS = r"""import json as __ps_json
import math as __ps_math
import os as __ps_os
import re as __ps_re
import sys as __ps_sys

__ps_UNSET = object()

class __ps_Fault(Exception):
    def __init__(self, code, line, column, message):
        self.code, self.line, self.column, self.message = code, line, column, message

def __ps_fail(code, line, column, message):
    raise __ps_Fault(code, line, column, message)

def __ps_raw(line, column, kind):
    if __ps_os.environ.get("PSEUDO_INTERACTIVE") == "1":
        __ps_sys.stderr.write("\x1ePS_INPUT:" + kind + "\n")
        __ps_sys.stderr.flush()
    value = __ps_sys.stdin.readline()
    if value == "":
        __ps_fail("RUN_INPUT_MISSING", line, column, "No hay más datos de entrada.")
    return value.rstrip("\r\n")

def __ps_read_number(line, column):
    value = __ps_raw(line, column, "NUMBER").strip()
    if not __ps_re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)", value):
        __ps_fail("RUN_INPUT_INVALID", line, column, "Se esperaba un número decimal finito.")
    number = float(value)
    if not __ps_math.isfinite(number):
        __ps_fail("RUN_INPUT_INVALID", line, column, "Se esperaba un número decimal finito.")
    return number

def __ps_read_text(line, column):
    return __ps_raw(line, column, "TEXT")

def __ps_format(value):
    if isinstance(value, bool):
        return "Verdadero" if value else "Falso"
    if isinstance(value, float):
        if not __ps_math.isfinite(value):
            return "NaN"
        if value == 0:
            return "0"
        if value.is_integer():
            return str(int(value))
        return format(value, ".15g")
    return str(value)

def __ps_write(*values):
    __ps_sys.stdout.write("".join(__ps_format(value) for value in values) + "\n")
    __ps_sys.stdout.flush()

def __ps_safe_int(value, line, column, label):
    if not isinstance(value, (int, float)) or not __ps_math.isfinite(value) or not float(value).is_integer() or abs(value) > 9007199254740991:
        __ps_fail("RUN_INVALID_INTEGER", line, column, label + " debe ser un entero seguro.")
    return int(value)

def __ps_new_array(size, line, column):
    size = __ps_safe_int(size, line, column, "Dimension")
    if size <= 0:
        __ps_fail("RUN_INVALID_DIMENSION", line, column, "Dimension requiere un tamaño positivo.")
    return [__ps_UNSET] * size

def __ps_index(array, index, line, column):
    index = __ps_safe_int(index, line, column, "El índice")
    if index < 1 or index > len(array):
        __ps_fail("RUN_BOUNDS", line, column, "Índice fuera del rango 1.." + str(len(array)) + ".")
    return index - 1

def __ps_get(array, index, line, column):
    slot = __ps_index(array, index, line, column)
    if array[slot] is __ps_UNSET:
        __ps_fail("RUN_UNINITIALIZED", line, column, "La posición del arreglo no se ha inicializado.")
    return array[slot]

def __ps_set(array, index, value, line, column):
    array[__ps_index(array, index, line, column)] = value

def __ps_div(left, right, line, column):
    if right == 0:
        __ps_fail("RUN_DIV_ZERO", line, column, "División entre cero.")
    value = left / right
    if not __ps_math.isfinite(value):
        __ps_fail("RUN_NONFINITE", line, column, "La operación produjo un número no finito.")
    return value

def __ps_mod(left, right, line, column):
    if right == 0:
        __ps_fail("RUN_DIV_ZERO", line, column, "Módulo entre cero.")
    value = left - int(left / right) * right
    if not __ps_math.isfinite(value):
        __ps_fail("RUN_NONFINITE", line, column, "La operación produjo un número no finito.")
    return value

def __ps_runtime_error(error):
    data = {"code": error.code, "line": error.line, "column": error.column, "message": error.message}
    __ps_sys.stderr.write("PSEUDO_RUNTIME_ERROR " + __ps_json.dumps(data, ensure_ascii=False) + "\n")
    __ps_sys.stderr.flush()
"""


JS_HELPERS = r"""const __ps_fs = require("node:fs");
const __ps_process = require("node:process");
const __ps_UNSET = Symbol("uninitialized");
class __ps_Fault extends Error {
  constructor(code, line, column, message) { super(message); this.code = code; this.line = line; this.column = column; }
}
function __ps_fail(code, line, column, message) { throw new __ps_Fault(code, line, column, message); }
function __ps_raw(line, column, kind) {
  if (__ps_process.env.PSEUDO_INTERACTIVE === "1") {
    __ps_process.stderr.write("\x1ePS_INPUT:" + kind + "\n");
  }
  const bytes = [];
  const byte = Buffer.alloc(1);
  while (true) {
    const count = __ps_fs.readSync(0, byte, 0, 1, null);
    if (count === 0) {
      if (bytes.length === 0) __ps_fail("RUN_INPUT_MISSING", line, column, "No hay más datos de entrada.");
      break;
    }
    if (byte[0] === 10) break;
    if (byte[0] !== 13) bytes.push(byte[0]);
  }
  return Buffer.from(bytes).toString("utf8");
}
function __ps_read_number(line, column) {
  const value = __ps_raw(line, column, "NUMBER").trim();
  if (!/^[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)$/.test(value)) __ps_fail("RUN_INPUT_INVALID", line, column, "Se esperaba un número decimal finito.");
  const number = Number(value);
  if (!Number.isFinite(number)) __ps_fail("RUN_INPUT_INVALID", line, column, "Se esperaba un número decimal finito.");
  return number;
}
function __ps_read_text(line, column) { return __ps_raw(line, column, "TEXT"); }
function __ps_format(value) {
  if (typeof value === "boolean") return value ? "Verdadero" : "Falso";
  if (typeof value === "number") {
    if (!Number.isFinite(value)) return "NaN";
    if (Object.is(value, -0) || value === 0) return "0";
    if (Number.isInteger(value)) return String(value);
    let text = value.toPrecision(15);
    if (text.includes("e")) {
      const parts = text.split("e");
      parts[0] = parts[0].replace(/\.?0+$/, "");
      return parts[0] + "e" + String(Number(parts[1]));
    }
    return text.replace(/\.?0+$/, "");
  }
  return String(value);
}
function __ps_write(...values) { __ps_process.stdout.write(values.map(__ps_format).join("") + "\n"); }
function __ps_safe_int(value, line, column, label) {
  if (!Number.isSafeInteger(value)) __ps_fail("RUN_INVALID_INTEGER", line, column, label + " debe ser un entero seguro.");
  return value;
}
function __ps_new_array(size, line, column) {
  size = __ps_safe_int(size, line, column, "Dimension");
  if (size <= 0) __ps_fail("RUN_INVALID_DIMENSION", line, column, "Dimension requiere un tamaño positivo.");
  return Array(size).fill(__ps_UNSET);
}
function __ps_index(array, index, line, column) {
  index = __ps_safe_int(index, line, column, "El índice");
  if (index < 1 || index > array.length) __ps_fail("RUN_BOUNDS", line, column, "Índice fuera del rango 1.." + array.length + ".");
  return index - 1;
}
function __ps_get(array, index, line, column) {
  const slot = __ps_index(array, index, line, column);
  if (array[slot] === __ps_UNSET) __ps_fail("RUN_UNINITIALIZED", line, column, "La posición del arreglo no se ha inicializado.");
  return array[slot];
}
function __ps_set(array, index, value, line, column) { array[__ps_index(array, index, line, column)] = value; }
function __ps_div(left, right, line, column) {
  if (right === 0) __ps_fail("RUN_DIV_ZERO", line, column, "División entre cero.");
  const value = left / right;
  if (!Number.isFinite(value)) __ps_fail("RUN_NONFINITE", line, column, "La operación produjo un número no finito.");
  return value;
}
function __ps_mod(left, right, line, column) {
  if (right === 0) __ps_fail("RUN_DIV_ZERO", line, column, "Módulo entre cero.");
  const value = left - Math.trunc(left / right) * right;
  if (!Number.isFinite(value)) __ps_fail("RUN_NONFINITE", line, column, "La operación produjo un número no finito.");
  return value;
}
function __ps_runtime_error(error) {
  const data = { code: error.code, line: error.line, column: error.column, message: error.message };
  __ps_process.stderr.write("PSEUDO_RUNTIME_ERROR " + JSON.stringify(data) + "\n");
}
"""


class Emitter:
    def __init__(self, target: str, symbols: list[Symbol], functions: list[Function]) -> None:
        self.target = target
        self.symbols = symbols
        self.functions = {item.normalized_name: item for item in functions}
        self.lines: list[str] = []
        self.source_map: list[dict[str, object]] = []
        self.current_scope = "global"
        self.temp_index = 0

    @staticmethod
    def _encoded(name: str) -> str:
        return "".join(f"{byte:02x}" for byte in name.encode("utf-8")) or "00"

    def variable(self, name: str) -> str:
        scope = self.current_scope
        if scope != "global" and (scope, name) not in {(symbol.scope, symbol.name) for symbol in self.symbols}:
            scope = "global"
        return "__ps_user_v_" + self._encoded(scope + "\x00" + name)

    def function(self, name: str) -> str:
        return "__ps_user_f_" + self._encoded(name)

    def emit(self, line: str = "", indent: int = 0, source: Span | None = None) -> None:
        self.lines.append("    " * indent + line)
        if source is not None:
            self.source_map.append(
                {
                    "generated_line": len(self.lines),
                    "source_span": source.to_dict(),
                }
            )

    def temp(self, suffix: str) -> str:
        self.temp_index += 1
        return f"__ps_tmp_{self.temp_index}_{suffix}"


def generate(program: Program, symbols: list[Symbol], target: str, *, validated: bool) -> GeneratedArtifact:
    if not validated:
        raise GenerationError("Solo se genera desde un AST semánticamente validado.")
    if target not in {"python", "javascript"}:
        raise GenerationError(f"Destino desconocido: {target}")
    emitter = Emitter(target, symbols, [stmt for stmt in program.body if isinstance(stmt, Function)])
    (PythonEmitter if target == "python" else JavaScriptEmitter)(emitter).program(program)
    source = "\n".join(emitter.lines).rstrip() + "\n"
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    return GeneratedArtifact(target, source, digest, emitter.source_map, ".py" if target == "python" else ".js")


class BaseEmitter:
    def __init__(self, emitter: Emitter) -> None:
        self.e = emitter

    def program(self, program: Program) -> None:
        raise NotImplementedError

    def functions(self, program: Program) -> None:
        for item in program.body:
            if isinstance(item, Function):
                self.function_definition(item)

    def function_definition(self, function: Function) -> None:
        raise NotImplementedError

    def statement(self, node: Statement, indent: int) -> None:
        raise NotImplementedError

    def expression(self, node: Expression) -> str:
        e = self.e
        if isinstance(node, Literal):
            if node.literal_kind == "string":
                return json.dumps(node.value, ensure_ascii=True)
            if node.literal_kind == "boolean":
                return (
                    ("True" if node.value else "False") if e.target == "python" else ("true" if node.value else "false")
                )
            value = float(node.value)
            return str(int(value)) if value.is_integer() else repr(value)
        if isinstance(node, Name):
            return e.variable(node.normalized)
        if isinstance(node, Unary):
            op = {"no": "not" if e.target == "python" else "!", "+": "+", "-": "-"}[node.operator]
            return f"({op}{self.expression(node.operand)})"
        if isinstance(node, Binary):
            left = self.expression(node.left)
            right = self.expression(node.right)
            op = node.operator
            if op == "/":
                return f"__ps_div({left}, {right}, {node.span.start_line}, {node.span.start_column})"
            if op == "%":
                return f"__ps_mod({left}, {right}, {node.span.start_line}, {node.span.start_column})"
            if op in {"y", "o"}:
                op = {"y": "and" if e.target == "python" else "&&", "o": "or" if e.target == "python" else "||"}[op]
            return f"({left} {op} {right})"
        if isinstance(node, Call):
            args = ", ".join(self.expression(item) for item in node.arguments)
            return f"{e.function(node.function)}({args})"
        if isinstance(node, Index):
            return f"__ps_get({self.expression(node.array)}, {self.expression(node.index)}, {node.span.start_line}, {node.span.start_column})"
        raise GenerationError(f"Expresión no soportada: {type(node).__name__}")

    def target_name(self, target: Name | Index) -> str:
        if isinstance(target, Name):
            return self.e.variable(target.normalized)
        raise GenerationError("El destino indexado debe generarse como asignación auxiliar.")


class PythonEmitter(BaseEmitter):
    def program(self, program: Program) -> None:
        self.e.lines.extend(PY_HELPERS.splitlines())
        self.functions(program)
        self.e.emit("try:")
        for statement in program.body:
            if not isinstance(statement, Function):
                self.statement(statement, 1)
        self.e.emit("except __ps_Fault as __ps_error:")
        self.e.emit("__ps_runtime_error(__ps_error)", 1)
        self.e.emit("__ps_sys.exit(70)", 1)
        self.e.emit("except Exception as __ps_error:")
        self.e.emit(
            "__ps_runtime_error(__ps_Fault('RUN_INTERNAL', 0, 0, str(__ps_error)))",
            1,
        )
        self.e.emit("__ps_sys.exit(71)", 1)

    def function_definition(self, function: Function) -> None:
        self.e.current_scope = f"function:{function.normalized_name}"
        params = ", ".join(self.e.variable(name) for name in function.normalized_parameters)
        self.e.emit(f"def {self.e.function(function.normalized_name)}({params}):", source=function.span)
        if not function.body:
            self.e.emit("pass", 1)
        else:
            for statement in function.body:
                self.statement(statement, 1)
        self.e.emit()
        self.e.current_scope = "global"

    def statement(self, node: Statement, indent: int) -> None:
        e = self.e
        if isinstance(node, Assign):
            if isinstance(node.target, Index):
                e.emit(
                    f"__ps_set({self.expression(node.target.array)}, {self.expression(node.target.index)}, {self.expression(node.value)}, {node.span.start_line}, {node.span.start_column})",
                    indent,
                    node.span,
                )
            else:
                e.emit(f"{self.target_name(node.target)} = {self.expression(node.value)}", indent, node.span)
        elif isinstance(node, Read):
            value = (
                f"__ps_read_text({node.span.start_line}, {node.span.start_column})"
                if node.text
                else f"__ps_read_number({node.span.start_line}, {node.span.start_column})"
            )
            if isinstance(node.target, Index):
                e.emit(
                    f"__ps_set({self.expression(node.target.array)}, {self.expression(node.target.index)}, {value}, {node.span.start_line}, {node.span.start_column})",
                    indent,
                    node.span,
                )
            else:
                e.emit(f"{self.target_name(node.target)} = {value}", indent, node.span)
        elif isinstance(node, Write):
            values = ", ".join(self.expression(value) for value in node.values)
            e.emit(f"__ps_write({values})", indent, node.span)
        elif isinstance(node, If):
            e.emit(f"if {self.expression(node.condition)}:", indent, node.span)
            self._body(node.then_body, indent + 1)
            if node.else_body:
                e.emit("else:", indent)
                self._body(node.else_body, indent + 1)
        elif isinstance(node, For):
            start, end, step = e.temp("start"), e.temp("end"), e.temp("step")
            line, col = node.span.start_line, node.span.start_column
            e.emit(
                f"{start} = __ps_safe_int({self.expression(node.start)}, {line}, {col}, 'Inicio de Para')",
                indent,
                node.span,
            )
            e.emit(f"{end} = __ps_safe_int({self.expression(node.end)}, {line}, {col}, 'Hasta de Para')", indent)
            if node.step:
                e.emit(f"{step} = __ps_safe_int({self.expression(node.step)}, {line}, {col}, 'Paso')", indent)
            else:
                e.emit(f"{step} = 1 if {start} <= {end} else -1", indent)
            e.emit(f"if {step} == 0:", indent)
            e.emit(f"__ps_fail('RUN_INVALID_STEP', {line}, {col}, 'Paso no puede ser cero.')", indent + 1)
            variable = e.variable(node.normalized_variable)
            e.emit(f"{variable} = {start}", indent)
            e.emit(f"while ({variable} <= {end} if {step} > 0 else {variable} >= {end}):", indent)
            self._body(node.body, indent + 1)
            e.emit(f"{variable} += {step}", indent + 1)
        elif isinstance(node, While):
            e.emit(f"while {self.expression(node.condition)}:", indent, node.span)
            self._body(node.body, indent + 1)
        elif isinstance(node, Dimension):
            e.emit(
                f"{e.variable(node.normalized_name)} = __ps_new_array({self.expression(node.size)}, {node.span.start_line}, {node.span.start_column})",
                indent,
                node.span,
            )
        elif isinstance(node, Return):
            e.emit(f"return {self.expression(node.value)}", indent, node.span)
        elif isinstance(node, ExprStatement):
            e.emit(self.expression(node.expression), indent, node.span)
        elif isinstance(node, Function):
            self.function_definition(node)

    def _body(self, statements: list[Statement], indent: int) -> None:
        if not statements:
            self.e.emit("pass", indent)
            return
        for statement in statements:
            self.statement(statement, indent)


class JavaScriptEmitter(BaseEmitter):
    def program(self, program: Program) -> None:
        self.e.lines.extend(JS_HELPERS.splitlines())
        globals_ = sorted(
            [symbol for symbol in self.e.symbols if symbol.scope == "global" and symbol.kind in {"variable", "array"}],
            key=lambda item: item.name,
        )
        if globals_:
            self.e.emit("let " + ", ".join(self.e.variable(item.name) for item in globals_) + ";")
        self.functions(program)
        self.e.emit("try {")
        for statement in program.body:
            if not isinstance(statement, Function):
                self.statement(statement, 1)
        self.e.emit("} catch (__ps_error) {")
        self.e.emit("if (__ps_error instanceof __ps_Fault) {", 1)
        self.e.emit("__ps_runtime_error(__ps_error);", 2)
        self.e.emit("__ps_process.exitCode = 70;", 2)
        self.e.emit("} else {", 1)
        self.e.emit("__ps_runtime_error(new __ps_Fault('RUN_INTERNAL', 0, 0, String(__ps_error)));", 2)
        self.e.emit("__ps_process.exitCode = 71;", 2)
        self.e.emit("}", 1)
        self.e.emit("}")

    def function_definition(self, function: Function) -> None:
        self.e.current_scope = f"function:{function.normalized_name}"
        params = ", ".join(self.e.variable(name) for name in function.normalized_parameters)
        self.e.emit(f"function {self.e.function(function.normalized_name)}({params}) {{", source=function.span)
        local_names = sorted(
            [
                symbol
                for symbol in self.e.symbols
                if symbol.scope == self.e.current_scope and symbol.kind != "parameter"
            ],
            key=lambda item: item.name,
        )
        if local_names:
            self.e.emit("let " + ", ".join(self.e.variable(item.name) for item in local_names) + ";", 1)
        for statement in function.body:
            self.statement(statement, 1)
        self.e.emit("}")
        self.e.emit()
        self.e.current_scope = "global"

    def statement(self, node: Statement, indent: int) -> None:
        e = self.e
        if isinstance(node, Assign):
            if isinstance(node.target, Index):
                e.emit(
                    f"__ps_set({self.expression(node.target.array)}, {self.expression(node.target.index)}, {self.expression(node.value)}, {node.span.start_line}, {node.span.start_column});",
                    indent,
                    node.span,
                )
            else:
                e.emit(f"{self.target_name(node.target)} = {self.expression(node.value)};", indent, node.span)
        elif isinstance(node, Read):
            value = (
                f"__ps_read_text({node.span.start_line}, {node.span.start_column})"
                if node.text
                else f"__ps_read_number({node.span.start_line}, {node.span.start_column})"
            )
            if isinstance(node.target, Index):
                e.emit(
                    f"__ps_set({self.expression(node.target.array)}, {self.expression(node.target.index)}, {value}, {node.span.start_line}, {node.span.start_column});",
                    indent,
                    node.span,
                )
            else:
                e.emit(f"{self.target_name(node.target)} = {value};", indent, node.span)
        elif isinstance(node, Write):
            values = ", ".join(self.expression(value) for value in node.values)
            e.emit(f"__ps_write({values});", indent, node.span)
        elif isinstance(node, If):
            e.emit(f"if ({self.expression(node.condition)}) {{", indent, node.span)
            self._body(node.then_body, indent + 1)
            if node.else_body:
                e.emit("} else {", indent)
                self._body(node.else_body, indent + 1)
            e.emit("}" if not node.else_body else "}", indent)
        elif isinstance(node, For):
            start, end, step = e.temp("start"), e.temp("end"), e.temp("step")
            line, col = node.span.start_line, node.span.start_column
            e.emit(
                f"const {start} = __ps_safe_int({self.expression(node.start)}, {line}, {col}, 'Inicio de Para');",
                indent,
                node.span,
            )
            e.emit(f"const {end} = __ps_safe_int({self.expression(node.end)}, {line}, {col}, 'Hasta de Para');", indent)
            if node.step:
                e.emit(f"const {step} = __ps_safe_int({self.expression(node.step)}, {line}, {col}, 'Paso');", indent)
            else:
                e.emit(f"const {step} = {start} <= {end} ? 1 : -1;", indent)
            e.emit(
                f"if ({step} === 0) __ps_fail('RUN_INVALID_STEP', {line}, {col}, 'Paso no puede ser cero.');", indent
            )
            variable = e.variable(node.normalized_variable)
            e.emit(f"{variable} = {start};", indent)
            e.emit(f"while ({step} > 0 ? {variable} <= {end} : {variable} >= {end}) {{", indent)
            self._body(node.body, indent + 1)
            e.emit(f"{variable} += {step};", indent + 1)
            e.emit("}", indent)
        elif isinstance(node, While):
            e.emit(f"while ({self.expression(node.condition)}) {{", indent, node.span)
            self._body(node.body, indent + 1)
            e.emit("}", indent)
        elif isinstance(node, Dimension):
            e.emit(
                f"{e.variable(node.normalized_name)} = __ps_new_array({self.expression(node.size)}, {node.span.start_line}, {node.span.start_column});",
                indent,
                node.span,
            )
        elif isinstance(node, Return):
            e.emit(f"return {self.expression(node.value)};", indent, node.span)
        elif isinstance(node, ExprStatement):
            e.emit(self.expression(node.expression) + ";", indent, node.span)
        elif isinstance(node, Function):
            self.function_definition(node)

    def _body(self, statements: list[Statement], indent: int) -> None:
        if not statements:
            self.e.emit(";", indent)
            return
        for statement in statements:
            self.statement(statement, indent)
