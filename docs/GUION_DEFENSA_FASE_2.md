# Guion de defensa — Fase 2

## Preparación antes de entrar

1. Arranca el entorno con `python3.12 scripts/manage.py start`.
2. Comprueba `python3.12 scripts/manage.py verify` y abre `http://127.0.0.1:5173`.
3. Continúa con la demostración de ejecución solo si el encabezado muestra **Sandbox verificado**. Si aparece **Sandbox no disponible**, corrige primero Docker Desktop → Settings → Resources → WSL Integration para la distro actual y repite `verify`; no anuncies una ejecución que no haya ocurrido.
4. Ten a mano `examples/C.psc`, `examples/D.psc` y `examples/official-cases.json`.

## Guion paso a paso

| Paso y acción en pantalla | Qué decir |
|---|---|
| 1. Abre la pestaña **Editor** y carga `examples/C.psc`. Pulsa **◎ Analizar**. | “Esta etapa empieza con el pseudocódigo. El editor manda el texto actual a la API local; no compara el texto con una respuesta del ejercicio. El hash identifica exactamente la fuente que se analizó.” |
| 2. En el inspector pulsa **Tokens** y selecciona un token. | “El lexer lee los caracteres y los clasifica como palabras reservadas, nombres, números, cadenas u operadores. Cada elemento tiene lexema, valor y posición para poder volver a la línea original.” |
| 3. Pulsa **AST**. Despliega `Program`, una asignación y el nodo `Binary` de una expresión. Señala `operator`, `izquierda` y `derecha`. | “El parser organiza las sentencias como nodos. En una expresión, el árbol muestra la precedencia: la multiplicación queda más profunda que la suma. Los paréntesis y la precedencia cambian el árbol que recorren los siguientes pasos.” |
| 4. Pulsa **Símbolos** y selecciona `n`, una variable de control o un acumulador. | “La semántica construye esta tabla durante el análisis. Aquí se ve el nombre, tipo inferido, ámbito, inicialización y referencias. Hay ámbito global y ámbito por función; los bloques Si y Para no crean ámbitos nuevos.” |
| 5. Vuelve al editor, reemplaza temporalmente una variable por `@`, y pulsa **◎ Analizar**. | “El lexer detecta el carácter inválido, informa su fase y ubicación y sugiere corregirlo. Como hay un error, la generación queda bloqueada.” |
| 6. Abre **Errores**, lee el diagnóstico y su sugerencia; selecciónalo para ver el foco en el editor. Pulsa **Exportar errores .txt**. | “El diagnóstico se puede seguir hasta el código fuente. La exportación contiene el hash, el error, su posición y una acción concreta; exportar errores no convierte un programa inválido en código ejecutable.” |
| 7. Corrige el carácter, analiza de nuevo y vuelve a **Pruebas**. Selecciona **C**. Ejecuta si el sandbox está verificado; después selecciona **D** y repite. | “La corrección invalida el análisis anterior, así que vuelvo a analizar. C y D se procesan con las entradas oficiales. Cada caso se ejecuta en Python y Node y se compara su salida completa.” |
| 8. Abre un resultado individual en la lista de pruebas. | “Este registro muestra entrada, salida esperada y real, errores, estado, duración y hash del artefacto. Las capturas y los números del informe deben provenir de esta corrida real.” |

## Cierre sugerido

“La Fase 2 separa tres tareas: reconocer el vocabulario, entender la estructura y revisar el significado de las variables y operaciones. El gestor devuelve errores localizados con sugerencias, mientras que el AST y la tabla de símbolos permiten explicar qué entendió el compilador. C y D muestran el prototipo con los casos académicos; la aceptación se documenta con las seis entradas de ambos programas en los dos runtimes.”

Las ejecuciones de C/D y sus capturas deben registrarse bajo la versión de código realmente mostrada. El estado de verificación se explica en [INFORME_FASE_2.md](INFORME_FASE_2.md).
