"""Traducción manual comentada del programa B para Python 3.12."""

import math
import re

_NUMERO = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)\Z")


def leer_numero():
    """Lee un valor finito de una línea de stdin."""
    entrada = input().strip()
    if not _NUMERO.fullmatch(entrada):
        raise ValueError("Se esperaba un número decimal finito.")
    valor = float(entrada)
    if not math.isfinite(valor):
        raise ValueError("Se esperaba un número decimal finito.")
    return valor


# Los mensajes aparecen en su propia línea, como en el pseudocódigo fuente.
print("Ingrese su nota final:")
nota = leer_numero()
print("Ingrese su porcentaje de asistencia:")
asistencia = leer_numero()

# Se conserva la primera condición y su Si anidado dentro de Sino.
if nota >= 6 and asistencia >= 75:
    print("Aprobado")
else:
    if nota >= 6 and asistencia < 75:
        print("Reprobado por asistencia")
    else:
        print("Reprobado por nota")
