# Pruebas extendidas del lenguaje

Esta suite agrega programas inéditos con combinaciones de construcciones más amplias que los ejemplos académicos A–E. No modifica la fuente ni los resultados oficiales de Fase 1.

## Cobertura

- Función recursiva, llamada antes de su definición, alias de retorno y rutas base/recursiva.
- Arreglos dinámicos de índice 1, lectura en ciclos `Para`, recorrido `Mientras`, máximo, promedio y conteo con `%`.
- Ciclos anidados, límites inclusivos, dirección automática ascendente/descendente y paso positivo explícito, operadores `Y/O/No`, precedencia, texto Unicode y ambas ramas de una condición.
- Funciones con parámetros locales, retorno numérico y textual, concatenación de cadenas y validación de tipos de argumentos.
- Ordenamiento burbuja de un arreglo y búsqueda lineal desde una función con parámetro-arreglo, incluidos duplicados y valor ausente.
- Errores sintácticos, identificadores indefinidos, tipos incompatibles, división constante por cero y uso no inicializado; cada uno comprueba código, fase y span.
- Fallos de ejecución con entrada inválida, división entre cero, dimensiones cero/negativas, acceso fuera de rango, elemento de arreglo sin inicializar y producto no finito; se ejecutan en Python y Node.

## Repetir las verificaciones

Con el entorno virtual y el sandbox disponibles:

```sh
.venv/bin/pytest -q backend/tests/test_extended_cases.py
python3.12 scripts/run_extended_acceptance.py
```

Pytest verifica las traducciones, spans y ejecuciones OCI reales. El script emite los resultados reproducibles en `reports/extended-acceptance-results.json` y `reports/extended-acceptance-results.md`. Cada ejecución válida guarda entrada, stdout esperado/real, stderr, estado, exit code, duración, versión del runtime y hashes de fuente/artefacto. Cada fallo controlado registra el código de error y su línea.

La aceptación registrada el 24 de octubre ejecutó **54/54 checks**: 6 compilaciones válidas, 28 ejecuciones válidas (14 casos en dos runtimes), 6 programas inválidos con diagnósticos/span exactos y 14 fallos de runtime controlados (7 casos en ambos runtimes). Incluye el algoritmo inédito de ordenamiento/búsqueda en arreglo y el desbordamiento finito→no finito.

La primera prueba de `1e308 * 10` expuso que los helpers comprobaban división/módulo pero la multiplicación directa podía imprimir `NaN`/`Infinity` como si terminara correctamente. El codegen ahora valida finitud para suma/resta/multiplicación numéricas y genera `RUN_NONFINITE`; después se regeneraron los snapshots y la aceptación volvió a correr en ambos destinos. Los detalles por ejecución están en los reportes JSON/Markdown.

La revalidación completa del 24 de octubre pasó `.venv/bin/pytest -q` (conteo final en `docs/VALIDATION_REPORT.md`, 90% de cobertura backend) y `python3.12 scripts/run_official_acceptance.py` (**30/30** oficiales A–E). Ordenamiento/búsqueda, dimensiones cero/negativas/fraccionarias y overflow ejecutan o fallan con diagnóstico esperado en ambos destinos. Ruff y `git diff --check` pasan. La única advertencia de pytest es la deprecación de `starlette.testclient` con `httpx`.

La suite toma sus fuentes y expectativas de `examples/extended/cases.json`; los `.psc` son fixtures de regresión para el lenguaje, no nuevas respuestas oficiales A–E.
