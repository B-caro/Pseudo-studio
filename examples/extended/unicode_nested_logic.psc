Inicio
LeerTexto etiqueta
Leer limite
acumulado = 0
Para fila = 1 Hasta limite Hacer
    Para columna = 1 Hasta 3 Paso 2 Hacer
        Si (etiqueta == "área" Y columna == 1) O fila == limite Entonces
            acumulado = acumulado + fila + columna
        Sino
            acumulado = acumulado + 1
        FinSi
    FinPara
FinPara
Escribir "Etiqueta: ", etiqueta, " / suma: ", acumulado
Fin
