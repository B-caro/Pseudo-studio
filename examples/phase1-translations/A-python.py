"""Traducción manual comentada del programa A para Python 3.12."""

import math
import re

_NUMERO = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)\Z")


def leer_numero():
    """Lee un renglón como número finito, siguiendo la sintaxis del lenguaje."""
    entrada = input().strip()
    if not _NUMERO.fullmatch(entrada):
        raise ValueError("Se esperaba un número decimal finito.")
    valor = float(entrada)
    if not math.isfinite(valor):
        raise ValueError("Se esperaba un número decimal finito.")
    return valor


def numero_a_texto(valor):
    """Evita mostrar .0 en resultados enteros, como el runtime del proyecto."""
    if valor.is_integer():
        return str(int(valor))
    return format(valor, ".15g")


# Cada Escribir del pseudocódigo termina una línea antes de solicitar el dato.
print("Ingrese el primer número:")
a = leer_numero()
print("Ingrese el segundo número:")
b = leer_numero()
print("Ingrese el tercer número:")
c = leer_numero()

# Se conservan los paréntesis y el orden de operaciones del programa A.
resultado = ((a + b) * c) - (a / b)

# Escribir concatena el literal con el resultado, sin un espacio automático.
print("El resultado es: " + numero_a_texto(resultado))
