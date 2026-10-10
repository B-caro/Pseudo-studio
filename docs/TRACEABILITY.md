# Matriz de trazabilidad — Pseudo / Studio

Esta matriz refleja pruebas ejecutadas al 2026-10-10. El PDF operativo gobierna RF/RNF; `fase_1.pdf` gobierna A–E. “Validado” identifica implementación real con evidencia ejecutable; los límites no se convierten en un cierre ficticio.

## Requisitos funcionales

| ID | Alcance exigido | Componentes / integración | Estado verificado | Evidencia ejecutada | Límite |
|---|---|---|---|
| RF-01 | Editor real, archivos y ejemplos | `frontend` editor + API/examples | Playwright: edición, cargar/guardar y comprobar que el análisis recibe la fuente editada | Validado | `frontend/e2e/workbench.spec.ts: abrir, editar, analizar, guardar y cargar .psc.` | — |
| RF-02 | Generar y descargar Python y JavaScript del mismo AST | compiler, generators, UI | tests de codegen + ejecución independiente de `.py` y `.js`; descarga e2e | Validado | `test_codegen.py; API/E2E traducen ambos destinos y descargan .py/.js.` | — |
| RF-03 | Lexer con tokens y spans reales | `backend/compiler/lexer.py` | unit tests de tokens, offsets, líneas, Unicode y errores | Validado | `backend/tests/test_lexer.py; spans/tokens reales.` | — |
| RF-04 | Parser, AST tipado y spans | `backend/compiler/parser.py`, AST | tests por producción, precedencia, serialización JSON y navegación | Validado | `backend/tests/test_parser.py; AST tipado y spans serializables.` | — |
| RF-05 | Tipos, inicialización, scopes, funciones, arrays | semantic analyzer | tests semánticos positivos y negativos con spans | Validado | `backend/tests/test_semantic.py; inicialización, scopes, funciones y arrays.` | — |
| RF-06 | Tabla de símbolos con referencias y estado | semantic analyzer + inspector | tests de scopes/lecturas/escrituras; selección de símbolo en UI | Validado | `test_semantic.py + E2E del panel Símbolos.` | — |
| RF-07 | Diagnósticos por fase con solución y ubicación | compiler/API/editor | casos N-01..N-09; API y navegación a línea/columna | Validado | `lexer/parser/semantic/API negativos y E2E de diagnóstico con foco.` | — |
| RF-08 | Bloquear generación/ejecución inválida u obsoleta | compile service, hashes, UI | pruebas 422, artefactos obsoletos y fuente modificada | Validado | `test_compiler_service.py/test_api.py bloquean inválidos y verifican hash de fuente/artefacto.` | — |
| RF-09 | Generadores autónomos Python 3 y JavaScript | `backend/generators/` | sintaxis de ambos intérpretes y ejecución de archivos descargados | Validado | `test_codegen.py; artefactos autónomos ejecutados por OCI y descargas E2E.` | — |
| RF-10 | I/O real y formato equivalente | runtime helpers Python/Node | diferencial de stdin/stdout, escapes, números y texto | Validado | `test_runner_integration.py; stdin/stdout real Python/Node y entradas diferenciales.` | — |
| RF-11 | Condiciones, lógica, precedencia y agrupación | parser, semántica, ambos codegens | tests de `Si`, anidación, `Y/O/No`, cortocircuito y bordes de B | Validado | `test_language_conformance.py, B boundary y A–E en ambos destinos.` | — |
| RF-12 | Consola y runner aislado con cancelación/cuotas | sandbox, API, WebSocket, UI | seguridad de OCI/VM, batch, stdin/stdout/stderr, cancelación y cuotas | Validado | `runner/API tests: VM WSL2, sin red, cuotas, cancelación e interacción WebSocket; E2E.` | — |
| RF-13 | Trazabilidad real de fases | API + panel de fases | integración verifica tiempos, hash y resultados calculados | Validado | `POST /analyze devuelve fases, duraciones y source hash; panel y E2E.` | — |
| RF-14 | Exportar fuente, artefactos, AST, símbolos, diagnósticos e informes | export service + UI | pruebas MIME, contenido y descarga de cada formato JSON/MD/PDF | Validado | `test_api.py prueba JSON/Markdown/PDF/MIME; E2E descarga código y reportes.` | — |
| RF-15 | `Para` inclusivo, paso y descenso | parser, semantic, codegens | unitarios y diferencial de límites/pasos | Validado | `test_parser.py/test_runner_integration.py; Para inclusivo, paso y descenso.` | — |
| RF-16 | Arrays `Dimension`, índice 1-based y bounds | parser, semantic, runtime helpers | unitarios y errores runtime para índices 0 y n+1 | Validado | `test_runner_integration.py; dimensión/indexado 1-based y errores en 0/n+1.` | — |
| RF-17 | Funciones, parámetros, retorno, scopes, recursión | parser, semantic, codegens | tests de firma, aridad, llamada adelantada, retorno y recursión | Validado | `test_semantic.py/test_codegen.py; scopes, retorno, llamadas adelantadas y recursión.` | — |
| RF-18 | Biblioteca A–E y suite Python/JS | `examples/`, test service | 15 casos oficiales × 2 destinos con stdout/stderr/status/hash por ejecución | Validado | `reports/acceptance-results.json/.md: 30 ejecuciones reales, 30 aprobadas; CLI y UI A–E.` | — |
| RF-19 | CRUD de proyectos y recuperación local | SQLite/project service + UI | tests API/SQLite y e2e crear/renombrar/duplicar/reabrir/eliminar | Validado | `test_project_store.py/test_api.py y E2E CRUD/recarga/autosave.` | — |
| RF-20 | Comparador y source maps | codegen + UI | tests de source map y selección fuente/destino en navegador | Validado | `test_codegen.py; E2E click en mapa de fuente y retorno al editor.` | — |
| RF-21 | Batch e interacción durante `Leer` | runner broker + WebSocket | pruebas con múltiples solicitudes `Leer`, respuesta, cancelación y lote | Validado | `runner/API/E2E: batch e input_requested real en WebSocket para ambos destinos.` | — |
| RF-22 | Registro trazable de ejecución sin exponer inputs | run service, reportes | assertions de hash, versión, runtime, tiempo, exit y privacidad de logs | Validado | `reportes incluyen inputs, stdout/stderr, status, exit, tiempo y hashes; test de logs sin fuente.` | — |
| RF-23 | Matriz editable de pruebas y diferencias | test service + UI | e2e editar caso, ejecutar destinos, comparar y descargar reporte | Validado | `API /tests/run produce diff y comparator Python↔Node; E2E edita/ejecuta/descarga.` | — |
| RF-24 | Autosave, aviso y restauración de borrador | frontend + persistencia | Playwright recarga/cierre/reapertura y cambios pendientes | Validado | `E2E recarga y reabre proyecto con fuente persistida y estado de autosave.` | — |
| RF-25 | Manual, gramática, ayuda y ejemplos comprobables | docs + UI | tests de consistencia gramática/parser y navegación de ayuda | Validado | `docs/gramatica.ebnf, docs/MANUAL.md y E2E ayuda/descarga EBNF.` | — |
| RF-26 | Modo defensa conectado al pipeline | UI + API | e2e siguiente fase con fuentes válidas e inválidas y resultado de servicio | Validado | `E2E ejecuta fases válidas e inválidas en Modo defensa y exporta resultado.` | — |
| RF-27 | API versionada, OpenAPI y errores coherentes | FastAPI/Pydantic | API tests positivos/negativos y validación del esquema OpenAPI | Validado | `test_api.py, Pydantic y OpenAPI FastAPI versionada.` | — |
| RF-28 | `Mientras`, booleanos, módulo, cadenas y comentarios | lexer/parser/semantic/codegen | conformidad gramatical y tests diferenciales inéditos | Validado | `tests de conformidad + 3 programas inéditos Python/Node con Mientras, `%` negativo y funciones.` | — |
| RF-29 | Estado real de servicios, runtimes y aislamiento | health service + UI | healthchecks de engine/imágenes; bloqueo explícito cuando no está listo | Validado | `manage.py verify/smoke, /health y UI: runners e imágenes reales detectados.` | — |

## Requisitos no funcionales

| ID | Condición | Capa | Evidencia de aceptación prevista |
|---|---|---|---|
| RNF-01 | Generación determinista, versiones y hashes | compiler/API/codegen | repetición produce hashes idénticos; modificación de fuente invalida artefactos | Validado | `source/artifact SHA-256 en compilación y acceptance reports deterministas.` | — |
| RNF-02 | Esquemas, sanitización, límites y excepciones | API | contratos Pydantic/OpenAPI, tamaños, errores HTTP y ausencia de stacktraces sensibles | Validado | `Schemas Pydantic, tamaño/unknown fields, 400/404/409/413/422/429/503 y sin traceback en test_api.py.` | — |
| RNF-03 | Sandbox rootless/VM, sin red, efímero, cuotas y cancelación | runtime/DevSecOps | pruebas de red, filesystem, procesos, memoria, salida, concurrencia y cancelación | Validado | `runner real en VM Docker Desktop WSL2: UID 10001, seccomp, NoNewPrivs, sin red/host/secrets, cuotas/OOM/timeout.` | — |
| RNF-04 | Privacidad local y telemetría desactivada | app/logging | configuración y auditoría de tráfico/dependencias | Validado | `servicios solo loopback; prueba de red del sandbox; fuentes no se escriben en logs.` | — |
| RNF-05 | Healthchecks y errores accionables | API/UI/runtime | estados de API, DB, engine y dos runtimes disponibles/no disponibles | Validado | `health incluye DB, daemon, imágenes y runtimes; prueba real verify/smoke.` | — |
| RNF-06 | Accesibilidad y responsividad | frontend | Playwright axe + revisión manual de teclado/foco/lector de pantalla y viewport móvil | Parcial | `Axe automatizado y teclado/foco pasan en 7 secciones; falta lector de pantalla manual.` | Falta revisión manual WCAG 2.2 AA con lector de pantalla/teclado asistivo. |
| RNF-07 | Logs estructurados con correlación y sin inputs sensibles | API/runtime | tests de request ID y redacción de datos | Validado | `X-Request-ID y prueba de redacción de fuente en logs.` | — |
| RNF-08 | SQLite, migraciones, backup y recuperación | projects | tests de migración, integridad, backup y restauración | Validado | `migraciones/CRUD/backup-restore SQLite probados; quick_check válido.` | — |
| RNF-09 | Tipado, lint, tests, lockfiles y CI | repositorio | CI completa desde instalación limpia; auditoría de dependencias | Validado | `requirements/npm lock, Ruff, tests, CI config y auditorías limpias; reproducción local clean install ejecutada.` | — |
| RNF-10 | Instrucciones reproducibles en Windows/macOS/Linux | scripts/docs | bootstrap y guía por plataforma; limitaciones declaradas y verificadas | Parcial | `guía incluye Windows WSL2/macOS/Linux; ejecución comprobada solo en WSL2.` | macOS nativo y Linux rootless no se ejecutaron; esta integración está documentada como pendiente. |
| RNF-11 | Fixtures, resultados, hashes, fecha y runtime reproducibles | reports/fixtures | manifiesto y reportes de cada ejecución oficial | Validado | `fixtures y reportes con fecha, input, stdout/stderr, status, runtime y hashes; 30/30.` | — |
| RNF-12 | Rendimiento y límites de seguridad sin excluir gramática | compiler/runtime | mediciones de 100/1000 líneas y carga concurrente con entorno declarado | Validado | `benchmark 100/1000 líneas con percentiles; concurrencia/cuotas y límites reales del runner.` | — |

## Fuentes académicas y control de autoridad

- El PDF operativo gobierna RF/RNF, gramática y semántica extendida.
- `Context/fase_1.pdf` gobierna el pseudocódigo literal A–E y sus tres datasets. Sus seis páginas fueron revisadas visualmente porque son páginas rasterizadas y no contienen texto extraíble.
- La tabla de resultados del PDF operativo define los resultados observables oficiales; se conserva el texto de solicitud de entrada de `fase_1.pdf` en las fuentes fixture.
- No se crea un Programa F ni se cambian algoritmos, entradas o salidas oficiales.
- El plan P0–P13 gobierna secuencia y cierre. Una fila solo pasa a verificada con implementación ejecutable, prueba real y evidencia.

## Resultado de la auditoría

- RF: 29/29 validados por pruebas reales del backend, runtimes o UI, con referencias individuales arriba.
- RNF: 10/12 validados; RNF-06 y RNF-10 quedan parciales por revisión manual de accesibilidad y ejecución fuera de WSL2.
- 195/205 tareas del plan verificadas; diez límites de verificación siguen abiertos y están enumerados en `docs/IMPLEMENTATION_STATUS.md`. El commit local de entrega es `415b54d`.
- A–E: 30/30 ejecuciones OCI reales; evidencia detallada en `reports/acceptance-results.json` y `reports/clean-install-acceptance-results.json`.
- No se declara 100% ni se ocultan las verificaciones ambientales no realizadas.
