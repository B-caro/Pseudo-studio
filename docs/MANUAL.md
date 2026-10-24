# Manual de Pseudo / Studio

## Flujo de trabajo

1. Abre **Editor**, escribe un programa completo `Inicio … Fin`, o selecciona un caso académico A–E en **Pruebas**.
2. Pulsa **Analizar**. El inspector muestra los tokens, AST, símbolos y diagnósticos que devuelve el compilador. Seleccionar un span lleva al editor.
3. Abre **Traducción** y pulsa **Traducir fuente actual**. Se generan Python y JavaScript desde el mismo AST validado. Los mapas enlazan líneas destino con la fuente; el hash cambia al editar.
4. En **Consola**, elige Python o JavaScript. La ejecución pasa por contenedores efímeros sin red y entrega stdin/stdout/stderr, estado, duración, versión y hashes. El modo interactivo solicita cada valor `Leer`; **Detener** cancela el proceso.
5. En **Pruebas**, ejecuta los tres datasets del programa seleccionado en ambos runtimes o edita entradas y salida esperada para tus propios casos. El informe compara la salida completa y se exporta a PDF, Markdown o JSON.
6. En **Proyectos**, crea un registro SQLite, renómbralo, duplica, elimina o recupéralo después de recargar. Los cambios sobre el proyecto actual se guardan automáticamente con control de versión.
7. **Defensa** avanza por fases de análisis usando la API real. **Ayuda** presenta la gramática que sirve el backend.

## Sintaxis de referencia

Cada sentencia termina en una nueva línea. La indentación ayuda a leer, pero los cierres (`FinSi`, `FinPara`, `FinMientras`, `FinFuncion`) determinan los bloques. `//` inicia comentario hasta el fin de línea.

```text
Inicio
Leer cantidad
Dimension datos[cantidad]
Para i = 1 Hasta cantidad Hacer
Leer datos[i]
FinPara
Escribir "Primer valor: ", datos[1]
Fin
```

Las palabras reservadas no distinguen mayúsculas/minúsculas; los identificadores sí y se normalizan a Unicode NFC. Los strings usan comillas dobles; los escapes implementados son `\\`, `\"`, `\n` y `\t`. La gramática completa está en [gramatica.ebnf](gramatica.ebnf).

### Tipos de datos y forma de los literales

Pseudo / Studio no tiene declaraciones explícitas de variables: la fase semántica infiere el tipo a partir de la primera asignación, de Leer/LeerTexto y de las operaciones donde se usa el valor.

| Categoría fuente | Escritura | Significado y restricciones |
|---|---|---|
| Entero | 0, 27, 2048 | Forma léxica numérica sin punto. Pertenece al tipo semántico number; no existe un tipo entero estático separado. En dimensiones e índices se exige además que el valor sea entero seguro y positivo cuando aplique. |
| Decimal | 3.14, .5, -0.25 | Forma léxica numérica con punto; el signo se analiza como operador unario. Usa punto, no coma, y no admite exponente. Pertenece a number. |
| Cadena | “Hola”, “línea seguida” | Tipo semántico string; delimitada por comillas dobles. Se admiten escapes para barra invertida, comilla doble, salto de línea y tabulación. |
| Lógico | Verdadero, Falso | Tipo semántico boolean; operadores Y, O y No. |

El análisis semántico usa una categoría numérica `number`: entero y decimal son formas léxicas, no tipos estáticos distintos. En Python, el generador conserva como `int` los literales sin parte fraccionaria y usa `float` para decimales y entradas `Leer`; JavaScript representa ambos como `Number`. Los tamaños e índices de arreglos se limitan a enteros seguros, donde ambos runtimes coinciden. Los identificadores comienzan con letra Unicode o guion bajo y continúan con letras, marcas combinantes, dígitos Unicode o guion bajo; se normalizan a NFC. La secuencia de dos barras diagonales inicia un comentario hasta el final de la línea.

### Expresiones y control

- Operadores aritméticos: `+`, `-`, `*`, `/`, `%` y `Modulo`; `%` sigue el resto con signo del dividendo.
- Comparación: `==`, `!=`, `<`, `<=`, `>` y `>=`. Lógica: `Y`, `O`, `No`, con cortocircuito.
- `Si expresión Entonces`, opcional `Sino`, `FinSi`.
- `Para i = inicio Hasta límite [Paso incremento] Hacer`; el límite es inclusivo. Sin `Paso`, la dirección se infiere de inicio/límite.
- `Mientras expresión Hacer … FinMientras`.
- `Dimension nombre[tamaño]`; índices válidos desde 1. El acceso fuera de rango produce diagnóstico runtime.
- `Leer destino` pide un número; `LeerTexto destino` pide texto. `Escribir` concatena sus expresiones sin separador automático.
- Las funciones admiten parámetros, llamada anidada/adelantada, recursión y `Retornar`. Las funciones con alias de retorno escriben el resultado en ese alias, como en E.

La validación de tipos, inicialización, aridad, ámbito y límites se describe en [DECISIONS.md](DECISIONS.md) y se ejecuta en la fase semántica. A–E conserva el pseudocódigo, los inputs y las salidas de `Context/fase_1.pdf` en [examples](../examples/README.md).

## API local

La raíz `/api/v1` documenta los schemas y rutas en Swagger local. `/health` da estado `ready` solo si SQLite, las dos imágenes OCI y sus controles de kernel pasan la verificación. Si indica `degraded`, consulta `python scripts/manage.py verify`; el runner nunca degrada a ejecución directa.

## Datos, backup y recuperación

El backend guarda proyectos e historial de ejecución en `data/projects.sqlite3`. El historial omite los valores de entrada. Crea una copia consistente incluso mientras el servicio está activo:

```sh
python scripts/manage.py backup
python scripts/manage.py backup --output data/backups/antes-de-migracion.sqlite3
```

Para recuperar una copia, detén la API, conserva el archivo actual como respaldo y copia el backup íntegro sobre `data/projects.sqlite3`. Al iniciar, SQLite aplica las migraciones pendientes. Los backups y datos locales están ignorados por Git.
