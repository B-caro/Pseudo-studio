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
let __ps_user_v_676c6f62616c0069, __ps_user_v_676c6f62616c006d6178, __ps_user_v_676c6f62616c006e, __ps_user_v_676c6f62616c006e756d65726f73, __ps_user_v_676c6f62616c0070726f6d6564696f, __ps_user_v_676c6f62616c0073756d61;
try {
    __ps_write("Ingrese la cantidad de n\u00fameros a ingresar:");
    __ps_user_v_676c6f62616c006e = __ps_read_number(3, 5);
    __ps_user_v_676c6f62616c006e756d65726f73 = __ps_new_array(__ps_user_v_676c6f62616c006e, 4, 5);
    __ps_user_v_676c6f62616c0073756d61 = 0;
    __ps_user_v_676c6f62616c006d6178 = 0;
    const __ps_tmp_1_start = __ps_safe_int(1, 7, 5, 'Inicio de Para');
    const __ps_tmp_2_end = __ps_safe_int(__ps_user_v_676c6f62616c006e, 7, 5, 'Hasta de Para');
    const __ps_tmp_3_step = __ps_tmp_1_start <= __ps_tmp_2_end ? 1 : -1;
    if (__ps_tmp_3_step === 0) __ps_fail('RUN_INVALID_STEP', 7, 5, 'Paso no puede ser cero.');
    __ps_user_v_676c6f62616c0069 = __ps_tmp_1_start;
    while (__ps_tmp_3_step > 0 ? __ps_user_v_676c6f62616c0069 <= __ps_tmp_2_end : __ps_user_v_676c6f62616c0069 >= __ps_tmp_2_end) {
        __ps_write("Ingrese el n\u00famero ", __ps_user_v_676c6f62616c0069, ":");
        __ps_set(__ps_user_v_676c6f62616c006e756d65726f73, __ps_user_v_676c6f62616c0069, __ps_read_number(9, 9), 9, 9);
        __ps_user_v_676c6f62616c0073756d61 = (__ps_user_v_676c6f62616c0073756d61 + __ps_get(__ps_user_v_676c6f62616c006e756d65726f73, __ps_user_v_676c6f62616c0069, 10, 23));
        if ((__ps_get(__ps_user_v_676c6f62616c006e756d65726f73, __ps_user_v_676c6f62616c0069, 11, 12) > __ps_user_v_676c6f62616c006d6178)) {
            __ps_user_v_676c6f62616c006d6178 = __ps_get(__ps_user_v_676c6f62616c006e756d65726f73, __ps_user_v_676c6f62616c0069, 12, 19);
        }
        __ps_user_v_676c6f62616c0069 += __ps_tmp_3_step;
    }
    __ps_user_v_676c6f62616c0070726f6d6564696f = __ps_div(__ps_user_v_676c6f62616c0073756d61, __ps_user_v_676c6f62616c006e, 15, 16);
    __ps_write("El promedio es: ", __ps_user_v_676c6f62616c0070726f6d6564696f);
    __ps_write("El n\u00famero mayor es: ", __ps_user_v_676c6f62616c006d6178);
} catch (__ps_error) {
    if (__ps_error instanceof __ps_Fault) {
        __ps_runtime_error(__ps_error);
        __ps_process.exitCode = 70;
    } else {
        __ps_runtime_error(new __ps_Fault('RUN_INTERNAL', 0, 0, String(__ps_error)));
        __ps_process.exitCode = 71;
    }
}
