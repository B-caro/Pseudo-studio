# Informe técnico — Fase 3: síntesis y ejecución

**Proyecto:** Pseudo / Studio · **Fecha:** 24 de octubre de 2026\
**Alcance:** generación desde AST, Python y JavaScript/Node, funciones y arreglos 1D, archivos de entrada/salida TXT y validación A–E.

## 1. Generación desde AST

`backend/compiler/service.py::compile_source` ejecuta lexer → parser → semántica y solo genera destinos cuando el programa no tiene errores. `backend/generators/codegen.py` recorre nodos tipados para producir artefactos completos y vistas de programa, mapas de fuente y hashes SHA-256. La pestaña Traducción presenta Python y JavaScript y mantiene sus descargas nativas `.py` y `.js`.

Los programas generados incluyen auxiliares para entrada numérica/textual, salida consistente, división y módulo controlados, arreglos 1-based, errores y acceso a stdin. No son resultados precalculados por ejercicio: el mismo recorrido de AST genera ambos destinos para cualquier programa aceptado por la gramática.

## 2. Contratos corregidos

- **Números:** los literales enteros del lexer son valores de doble precisión. Python conserva la forma flotante (`1.0`) como JavaScript `Number`, evitando que Python aplique enteros arbitrarios cerca de `2^53`. La prueba `9007199254740992 + 1` ejecuta ambos destinos de forma aislada y verifica su mismo resultado.
- **Arreglos por valor:** la semántica infiere el uso de un parámetro como arreglo y rechaza pasarle un escalar. Los emisores copian el contenedor 1D al entrar a la función (`list` / `slice`), para que modificar el parámetro no cambie el arreglo original. La prueba diferencial se ejecuta en ambos runtimes aislados.
- **Errores:** las sugerencias de lexer, parser y semántica son contextuales; los spans con emoji se convierten correctamente al foco del editor.

## 3. Flujo de archivos TXT

La entrada de `.psc` y `.txt` se procesa como UTF-8 estricto, acepta CRLF y elimina un BOM inicial. Una secuencia UTF-8 inválida produce un aviso y conserva la fuente editada. Las descargas API incluyen:

| Descarga | Contenido |
|---|---|
| `python-txt` | Bytes idénticos al artefacto Python completo actual, con runtime auxiliar. |
| `javascript-txt` | Bytes idénticos al artefacto JavaScript/Node completo actual. |
| `diagnostics-txt` | Estado, hash, versión, cantidad y lista determinista con fase, código, ubicación, mensaje y sugerencia. También informa que no hay errores para una fuente válida. |

Una fuente inválida puede producir el reporte de errores TXT, pero no un archivo de código. El frontend conecta controles de descarga a los endpoints reales; la prueba API compara cada TXT con su salida nativa y confirma el bloqueo de código inválido.

## 4. Casos A–E y runtimes

El anexo contiene cinco programas y quince datasets. La aceptación completa requiere quince × dos = 30 ejecuciones aisladas con stdout, stderr, status/exit, duración, entrada, runtime y hashes. `scripts/run_official_acceptance.py`, `reports/acceptance-results.json` y las pruebas de `backend/tests/test_runner_integration.py` implementan y conservan el oráculo.

En la revalidación del 24 de octubre, `python3.12 scripts/manage.py verify` pasó con Docker Desktop VM, imágenes presentes y controles internos activos. `python3.12 scripts/run_official_acceptance.py` ejecutó **30/30** casos oficiales reales en OCI: 15 datasets × Python/Node. stdout coincide exactamente, stderr queda vacío y exit code es 0; cada registro incluye inputs, tiempos, versiones y hashes en `reports/acceptance-results.json/.md`.

## 5. Pruebas de entrega

La suite completa terminó con los conteos vigentes indicados en `docs/VALIDATION_REPORT.md`; la cobertura backend reportada es 90%. `npm run build` pasa y `npm run test:e2e` ejecuta **10/10** flujos Chromium, incluyendo entrada TXT, descargas, diagnóstico, corrección y nueva traducción, ejecución Python/Node, entrada interactiva y los 15 casos A–E desde la interfaz. `python3.12 scripts/run_extended_acceptance.py` agrega **54/54** verificaciones de compilación, ejecución, negativos y errores runtime. El flujo API descarga el TXT, verifica igualdad con el `.py/.js` completo y ejecuta los bytes descargados bajo OCI. Todos los comandos/resultados se detallan en [VALIDATION_REPORT.md](VALIDATION_REPORT.md).

## 6. Estado frente a la rúbrica

| Criterio | Estado de implementación | Evidencia que falta para cierre |
|---|---|---|
| Generación desde AST (20%) | Dos emitters visitan nodos; errores bloquean generación; hashes y source maps disponibles. | Verificado con suite backend, casos inéditos y aceptación extendida 54/54, incluido `RUN_NONFINITE`. |
| Dos destinos (20%) | Python 3 y JavaScript en Node.js, cada uno con artefacto autónomo. | Verificado en OCI; las descargas TXT y los artefactos completos se comparan y ejecutan. |
| Arreglos y funciones (20%) | Scopes, inferencia, aridad, retorno, arrays 1D y copias al llamar. | Verificado con regresiones de arrays/funciones y casos de borde en ambos runtimes. |
| Funcionamiento A–E (25%) | Entrada TXT, salidas de código TXT y reporte TXT de errores en API/UI. | E2E 10/10 carga/exporta/ejecuta y valida; aceptación oficial OCI 30/30. |
| Validación por lenguaje (15%) | Fixtures y runner comparan 15 datasets en Python + Node. | Verificado: 30/30 registros en `reports/acceptance-results.json/.md`. |

La validación técnica local de los criterios de la tabla quedó ejecutada. Esto no certifica la presentación académica final: siguen pendientes la revisión/paginación del DOCX con datos reales, el ensayo humano y la defensa/entrega institucional. También siguen abiertos los gates globales de lector de pantalla, macOS/Linux rootless y CI remota dispensada, según [REMAINING_GATES.md](REMAINING_GATES.md). El guion de recorrido está en [GUION_DEFENSA_FASE_3.md](GUION_DEFENSA_FASE_3.md).
