Inicio
Leer cantidad
Dimension valores[cantidad]
suma = 0
Para i = 1 Hasta cantidad Hacer
    Leer valores[i]
    suma = suma + valores[i]
FinPara
promedio = suma / cantidad
mayor = valores[1]
pares_positivos = 0
i = 1
Mientras i <= cantidad Hacer
    Si valores[i] > mayor Entonces
        mayor = valores[i]
    FinSi
    Si valores[i] > 0 Y valores[i] % 2 == 0 Entonces
        pares_positivos = pares_positivos + 1
    Sino
        pares_positivos = pares_positivos
    FinSi
    i = i + 1
FinMientras
Escribir "Promedio=", promedio
Escribir "Mayor=", mayor
Escribir "Pares positivos=", pares_positivos
Fin
