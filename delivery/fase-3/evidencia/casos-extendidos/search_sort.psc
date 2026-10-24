Inicio
Funcion posicion = Buscar(datos, cantidad, objetivo)
    posicion = 0
    Para indice = 1 Hasta cantidad Hacer
        Si datos[indice] == objetivo Entonces
            Si posicion == 0 Entonces
                posicion = indice
            FinSi
        FinSi
    FinPara
    Retornar posicion
FinFuncion

Leer cantidad
Dimension valores[cantidad]
Para indice = 1 Hasta cantidad Hacer
    Leer valores[indice]
FinPara

// Ordenamiento burbuja ascendente con límites inclusivos.
Para pasada = 1 Hasta cantidad - 1 Hacer
    Para indice = 1 Hasta cantidad - pasada Hacer
        siguiente = indice + 1
        Si valores[indice] > valores[siguiente] Entonces
            temporal = valores[indice]
            valores[indice] = valores[siguiente]
            valores[siguiente] = temporal
        FinSi
    FinPara
FinPara

Leer objetivo
posicion = Buscar(valores, cantidad, objetivo)
Escribir "Ordenados:"
Para indice = 1 Hasta cantidad Hacer
    Escribir valores[indice]
FinPara
Escribir "Posición=", posicion
Fin
