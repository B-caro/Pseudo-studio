import json as __ps_json
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
try:
    __ps_write("Ingrese la cantidad de n\u00fameros a ingresar:")
    __ps_user_v_676c6f62616c006e = __ps_read_number(3, 5)
    __ps_user_v_676c6f62616c006e756d65726f73 = __ps_new_array(__ps_user_v_676c6f62616c006e, 4, 5)
    __ps_user_v_676c6f62616c0073756d61 = 0
    __ps_user_v_676c6f62616c006d6178 = 0
    __ps_tmp_1_start = __ps_safe_int(1, 7, 5, 'Inicio de Para')
    __ps_tmp_2_end = __ps_safe_int(__ps_user_v_676c6f62616c006e, 7, 5, 'Hasta de Para')
    __ps_tmp_3_step = 1 if __ps_tmp_1_start <= __ps_tmp_2_end else -1
    if __ps_tmp_3_step == 0:
        __ps_fail('RUN_INVALID_STEP', 7, 5, 'Paso no puede ser cero.')
    __ps_user_v_676c6f62616c0069 = __ps_tmp_1_start
    while (__ps_user_v_676c6f62616c0069 <= __ps_tmp_2_end if __ps_tmp_3_step > 0 else __ps_user_v_676c6f62616c0069 >= __ps_tmp_2_end):
        __ps_write("Ingrese el n\u00famero ", __ps_user_v_676c6f62616c0069, ":")
        __ps_set(__ps_user_v_676c6f62616c006e756d65726f73, __ps_user_v_676c6f62616c0069, __ps_read_number(9, 9), 9, 9)
        __ps_user_v_676c6f62616c0073756d61 = (__ps_user_v_676c6f62616c0073756d61 + __ps_get(__ps_user_v_676c6f62616c006e756d65726f73, __ps_user_v_676c6f62616c0069, 10, 23))
        if (__ps_get(__ps_user_v_676c6f62616c006e756d65726f73, __ps_user_v_676c6f62616c0069, 11, 12) > __ps_user_v_676c6f62616c006d6178):
            __ps_user_v_676c6f62616c006d6178 = __ps_get(__ps_user_v_676c6f62616c006e756d65726f73, __ps_user_v_676c6f62616c0069, 12, 19)
        __ps_user_v_676c6f62616c0069 += __ps_tmp_3_step
    __ps_user_v_676c6f62616c0070726f6d6564696f = __ps_div(__ps_user_v_676c6f62616c0073756d61, __ps_user_v_676c6f62616c006e, 15, 16)
    __ps_write("El promedio es: ", __ps_user_v_676c6f62616c0070726f6d6564696f)
    __ps_write("El n\u00famero mayor es: ", __ps_user_v_676c6f62616c006d6178)
except __ps_Fault as __ps_error:
    __ps_runtime_error(__ps_error)
    __ps_sys.exit(70)
except Exception as __ps_error:
    __ps_runtime_error(__ps_Fault('RUN_INTERNAL', 0, 0, str(__ps_error)))
    __ps_sys.exit(71)
