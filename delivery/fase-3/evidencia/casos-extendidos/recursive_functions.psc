Inicio
LeerTexto modo
Leer numero
Si modo == "factorial" Y numero >= 0 Entonces
    Escribir "Factorial de ", numero, " = ", Factorial(numero)
Sino
    Escribir "Entrada no válida"
FinSi
Funcion factorial = Factorial(n)
    Si n <= 1 Entonces
        factorial = 1
    Sino
        factorial = n * Factorial(n - 1)
    FinSi
    Retornar factorial
FinFuncion
Fin
