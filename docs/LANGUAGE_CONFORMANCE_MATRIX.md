# Matriz de conformidad del lenguaje

**Actualizada:** 24 de octubre de 2026. Esta matriz relaciona reglas implementadas con ejemplos y diagnósticos del compilador. Los programas inválidos bloquean la generación; una salida de análisis parcial nunca se considera ejecutable.

## Convenciones comprobadas

- Las palabras reservadas no distinguen mayúsculas y minúsculas. Los identificadores sí distinguen caso y se normalizan a Unicode NFC.
- Los spans del backend son offsets de puntos de código Python, con línea y columna desde 1. La UI convierte offsets a unidades UTF-16 de CodeMirror antes de seleccionar texto.
- `number` representa números finitos de doble precisión; los enteros y decimales son formas léxicas del mismo tipo. `Leer` obtiene un número; `LeerTexto` obtiene una cadena. `Escribir` concatena sin separador implícito.
- Los comentarios usan `//`; las cadenas usan comillas dobles y escapes documentados en [gramatica.ebnf](gramatica.ebnf). Las líneas pueden terminar en LF o CRLF.
- El cargador de archivos usa UTF-8 estricto, quita un BOM inicial y conserva el contenido restante, incluidas tildes y finales de línea. Bytes UTF-8 inválidos se rechazan antes de reemplazar la fuente actual.

## Producciones, nodos y pruebas

| Familia | Reconocimiento / nodo | Ejemplo válido | Caso inválido y resultado | Pruebas de referencia |
|---|---|---|---|---|
| Programa | `Inicio … Fin` → `Program` | `Inicio\nEscribir 1\nFin` | Falta `Fin` → `SYN_UNEXPECTED_TOKEN`, sin artefactos | `test_parser.py`; `test_compiler_service.py` |
| Identificadores y comentarios | `IDENT`, comentario sin token | `área = 1 // nota` | Carácter fuera del léxico → `LEX_INVALID_CHAR` con ubicación y sugerencia | `test_lexer.py` |
| Números | `NUMBER` | `12`, `3.25`, `.5` | Literal no finito o no reconocido → `LEX_INVALID_NUMBER` / `LEX_INVALID_CHAR` | `test_lexer.py`; `test_codegen.py` |
| Cadenas y booleanos | `STRING`, `BOOL` → `Literal` | `Escribir "Hola", Verdadero` | Escape inválido o cierre ausente → `LEX_INVALID_ESCAPE` / `LEX_UNTERMINATED_STRING` | `test_lexer.py` |
| Lectura / escritura | `Leer`, `LeerTexto`, `Escribir` → `Read`, `Write` | `LeerTexto nombre` y `Escribir "Hola ", nombre` | Asignar número y texto al mismo nombre → `SEM_TYPE_MISMATCH` | `test_semantic.py`; `test_runner_integration.py` |
| Asignación y llamadas | `IDENT = expresión` / `Call` → `Assign`, `ExprStatement` | `doble = Duplicar(4)` | Nombre no definido → `SEM_UNDEFINED_IDENTIFIER`; aridad distinta → `SEM_WRONG_ARITY` | `test_semantic.py` |
| Expresiones | Pratt parser; precedencia `No`, `* / Modulo`, `+ -`, comparación, `Y`, `O` → `Unary`, `Binary` | `1 + 2 * 3` agrupa `1 + (2 * 3)` | Operando faltante → `SYN_EXPECTED_EXPRESSION`; divisor constante 0 → `SEM_DIV_ZERO` | `test_parser.py`; `test_language_conformance.py` |
| Condicional | `Si … Entonces … [Sino …] FinSi` → `If` | Condicional anidado con ramas completas | Falta `FinSi` → error sintáctico con sugerencia de cierre | `test_parser.py`; fixtures B/E |
| Ciclos | `Mientras` / `Para … Hasta … [Paso …]` → `While`, `For` | Límite inclusivo y paso descendente | Paso constante cero → `SEM_INVALID_STEP`; condición no booleana → `SEM_TYPE_MISMATCH` | `test_semantic.py`; integración OCI |
| Arreglos 1D | `Dimension a[n]`, `a[i]` → `Dimension`, `Index` | Dimensión positiva y asignaciones a índices `1..n` | Dimensión inválida → `SEM_INVALID_DIMENSION`; índice dinámico fuera de rango → `RUN_BOUNDS` | `test_semantic.py`; integración OCI |
| Funciones | `Funcion f(p) … Retornar … FinFuncion` → `Function`, `Return` | Función adelantada o recursiva con retorno | Nombre duplicado, retorno fuera de función o aridad incorrecta → `SEM_DUPLICATE_FUNCTION`, `SEM_RETURN_OUTSIDE_FUNCTION`, `SEM_WRONG_ARITY` | `test_semantic.py`; fixtures E |
| Parámetro arreglo | Tipo inferido por indexación y llamadas | `Primero(datos)` donde `datos` es un arreglo | Pasar un escalar a un parámetro usado como arreglo → `SEM_TYPE_MISMATCH` | `test_semantic.py`; codegen e integración OCI |

## Recuperación y límites de generación

`Parser._parse_block` sincroniza en saltos de línea y terminadores de bloque. La regresión `test_multiple_nested_errors_recover_and_keep_hints_with_exact_spans` introduce errores léxicos y dos errores sintácticos dentro de un `Si/Sino`: el análisis termina, informa ambos renglones y deja `translatable=false` con `artifacts={}`. Los diagnósticos conservan fase, código, mensaje, span y sugerencia. `Diagnostic` añade una sugerencia por código cuando una fase no proporciona una más contextual; el parser construye una sugerencia basada en el elemento faltante.

El compilador hace una pasada léxica lineal sobre caracteres; el parser descendente/Pratt visita la secuencia de tokens manteniendo la pila de bloques; la tabla semántica usa claves `(ámbito, nombre)` en diccionario y recorre los nodos del programa. La complejidad temporal típica es O(n) en el tamaño de la fuente/AST para el subconjunto definido, con búsquedas de símbolos promedio O(1). La recursión de funciones y la profundidad de anidación consumen pila; la suite también contiene una regresión de 120 paréntesis y 1,000 sentencias.

## Alcance de los tipos y ámbitos

Los tipos estáticos son `number`, `string`, `boolean`, `array` y `unknown` durante inferencia. La tabla conserva categoría, tipo, ámbito, inicialización, referencias y contadores de lectura/escritura. Hay ámbito global y ámbito local por función; no se atribuyen ámbitos independientes a bloques `Si` o ciclos. Las variables se crean al asignarse o leerse y se comprueba inicialización antes de lectura. Las funciones se predeclaran, lo que permite llamadas adelantadas; sus parámetros se restringen por el cuerpo y los argumentos.

Los parámetros escalares se asignan por valor en ambos destinos. Un arreglo fuente es un contenedor 1D de valores escalares: el emisor copia ese contenedor al entrar a la función (`list(p)` en Python y `p.slice()` en JavaScript). La mutación del parámetro no afecta el arreglo original; la regresión diferencial se ejecutó en los dos runtimes OCI en la revalidación del 24 de octubre.

## Ejecución reproducible

```bash
.venv/bin/pytest -q backend/tests/test_lexer.py backend/tests/test_parser.py backend/tests/test_semantic.py backend/tests/test_language_conformance.py backend/tests/test_codegen.py
```

Los casos que invoquen ambos runtimes están declarados en `backend/tests/test_runner_integration.py`; requieren que `python3.12 scripts/manage.py verify` confirme el aislamiento OCI. El 24 de octubre ese control pasó en Docker Desktop VM. Los resultados vigentes se registran en [VALIDATION_REPORT.md](VALIDATION_REPORT.md); las menciones a indisponibilidad de Docker en otros informes son contexto histórico de cortes anteriores.
