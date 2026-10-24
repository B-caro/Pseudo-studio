Inicio
LeerTexto nombre
Leer valor
saludo = Saludar(nombre)
resultado = Transformar(valor)
Escribir saludo
Si (resultado % 2 == 0) Y (nombre != "") Entonces
    Escribir "Mitad=", resultado / 2
Sino
    Escribir "Resultado=", resultado
FinSi
Funcion texto = Saludar(persona)
    Si persona == "" Entonces
        texto = "Hola, invitado"
    Sino
        texto = "Hola, " + persona
    FinSi
    Retornar texto
FinFuncion
Funcion Transformar(x)
    local = x * 3 - 1
    Retornar local
FinFuncion
Fin
