const __ps_fs = require("node:fs");
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
let __ps_user_v_676c6f62616c00616c74757261, __ps_user_v_676c6f62616c006172656143616c63756c616461, __ps_user_v_676c6f62616c0062617365, __ps_user_v_676c6f62616c00726573756c7461646f;
function __ps_user_f_43616c63756c617241726561(__ps_user_v_66756e6374696f6e3a43616c63756c6172417265610062617365, __ps_user_v_66756e6374696f6e3a43616c63756c61724172656100616c74757261) {
    let __ps_user_v_66756e6374696f6e3a43616c63756c6172417265610061726561;
    __ps_user_v_66756e6374696f6e3a43616c63756c6172417265610061726561 = (__ps_user_v_66756e6374696f6e3a43616c63756c6172417265610062617365 * __ps_user_v_66756e6374696f6e3a43616c63756c61724172656100616c74757261);
    return __ps_user_v_66756e6374696f6e3a43616c63756c6172417265610061726561;
}

function __ps_user_f_436c617369666963617241726561(__ps_user_v_66756e6374696f6e3a436c6173696669636172417265610061726561) {
    let __ps_user_v_66756e6374696f6e3a436c61736966696361724172656100636c6173696669636163696f6e;
    if ((__ps_user_v_66756e6374696f6e3a436c6173696669636172417265610061726561 > 50)) {
        __ps_user_v_66756e6374696f6e3a436c61736966696361724172656100636c6173696669636163696f6e = "Grande";
    } else {
        __ps_user_v_66756e6374696f6e3a436c61736966696361724172656100636c6173696669636163696f6e = "Peque\u00f1a";
    }
    return __ps_user_v_66756e6374696f6e3a436c61736966696361724172656100636c6173696669636163696f6e;
}

try {
    __ps_write("Ingrese la base:");
    __ps_user_v_676c6f62616c0062617365 = __ps_read_number(17, 5);
    __ps_write("Ingrese la altura:");
    __ps_user_v_676c6f62616c00616c74757261 = __ps_read_number(19, 5);
    __ps_user_v_676c6f62616c006172656143616c63756c616461 = __ps_user_f_43616c63756c617241726561(__ps_user_v_676c6f62616c0062617365, __ps_user_v_676c6f62616c00616c74757261);
    __ps_user_v_676c6f62616c00726573756c7461646f = __ps_user_f_436c617369666963617241726561(__ps_user_v_676c6f62616c006172656143616c63756c616461);
    __ps_write("El \u00e1rea es: ", __ps_user_v_676c6f62616c006172656143616c63756c616461);
    __ps_write("Clasificaci\u00f3n: ", __ps_user_v_676c6f62616c00726573756c7461646f);
} catch (__ps_error) {
    if (__ps_error instanceof __ps_Fault) {
        __ps_runtime_error(__ps_error);
        __ps_process.exitCode = 70;
    } else {
        __ps_runtime_error(new __ps_Fault('RUN_INTERNAL', 0, 0, String(__ps_error)));
        __ps_process.exitCode = 71;
    }
}
