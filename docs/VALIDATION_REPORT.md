# Informe de validación — Pseudo / Studio

## Cierre de brechas de Fases 2 y 3 — 2026-10-24

Esta sección registra la revalidación más reciente sobre el árbol de trabajo actual y **sustituye los reportes históricos de indisponibilidad de OCI** que siguen citados abajo con su fecha original.

- `python3.12 scripts/manage.py verify`: exit 0. Docker 28.1.1 usa la frontera `docker-desktop-vm`; imágenes Python 3.12.14 y Node v22.22.2 disponibles. Ambos pasan como UID no root, `NoNewPrivs`, seccomp activo y cero capabilities. Límites declarados: 5 s, 256 MiB, 1 CPU, 64 procesos y 1 MiB de salida.
- `python3.12 scripts/manage.py start`, `python3.12 scripts/manage.py smoke`, `python3.12 scripts/manage.py stop`: arranque y smoke reales pasan en ambos runtimes (`OK=42`); hash Python `c6ed893305c9242427dd3a3d27eb0a30997d7e4a51f93bbe08b7a01f75f03572`, JavaScript `0f82f4912b1b4d3e9d8280638c30b97f143a51b21e3f0a1311fdd032d5fd7765`. Al terminar se detuvieron frontend y API; los puertos 8000/5173 quedaron libres.
- `.venv/bin/pytest -q`: **94 passed y 91 subtests passed**, cobertura backend 90%; un warning de deprecación de Starlette TestClient/httpx, sin fallos (165,14 s).
- `npm run test:e2e`: **10/10** Playwright pasan en Chromium, sin reintentos. Incluye teclado y axe, las ocho secciones, carga/análisis, exportaciones TXT, error→corrección→nuevo análisis, ejecución Python/Node, stdin interactivo, proyectos, casos A–E y viewport móvil. Reporte HTML: `frontend/playwright-report/`; estado: `frontend/test-results/.last-run.json`.
- `npm run build`: TypeScript y Vite pasan. `.venv/bin/ruff check backend scripts`, `.venv/bin/ruff format --check backend scripts` y `git diff --check`: pasan.
- `python3.12 scripts/run_official_acceptance.py`: **30/30** ejecuciones aisladas A–E Python/Node. `python3.12 scripts/run_extended_acceptance.py`: **54/54** checks: 28 ejecuciones válidas, seis negativos con spans y catorce errores de runtime controlados. Incluye overflow numérico detectado por una prueba de regresión y corregido con `RUN_NONFINITE`. Los registros incluyen entradas, salidas, stderr, estado, duración y hashes en `reports/acceptance-results.json` y `reports/extended-acceptance-results.json`.
- `python3.12 scripts/run_phase1_manual_acceptance.py`: **12/12** casos A/B manuales con stdin agrupado en los runtimes locales; no se cuentan como OCI.
- `python3.12 scripts/benchmark_compile.py`: 30 mediciones por clase/tamaño. Compilación válida: 100 líneas p50/p95 2.758/3.475 ms; 1.000 líneas 37.494/50.703 ms. Recuperación de errores: 100 líneas y 98 diagnósticos 2.246/4.056 ms; 1.000 líneas y 998 diagnósticos 18.491/24.139 ms. Entorno: Python 3.12.3, WSL2, 12 CPU. JSON y Markdown: `reports/compiler-performance.*`.
- Evidencia visual del navegador: `reports/phase2-execution-c.png` y `reports/phase2-execution-d.png`; A/B manuales: `reports/phase1-execution-python.png` y `reports/phase1-execution-javascript.png`.

Los archivos `.txt` de Python/JavaScript son los artefactos completos generados por el compilador, byte por byte iguales a `.py/.js`; las pruebas API descargan esos bytes y los ejecutan en OCI. El E2E valida sus descargas, la carga UTF-8/BOM/CRLF y el reporte TXT de errores. Los detalles por requisito están en [TRACEABILITY.md](TRACEABILITY.md) y las fuentes/decisiones en [LANGUAGE_CONFORMANCE_MATRIX.md](LANGUAGE_CONFORMANCE_MATRIX.md) y [DECISIONS.md](DECISIONS.md).

`python3.12 scripts/build_phase3_package.py` produjo `delivery/fase-3/` con 74 archivos registrados; los 74 hashes verifican, los diez pares nativos/TXT son idénticos y los diez `.py/.js` del paquete coinciden con los hashes de artefacto de la corrida oficial 30/30. Se conservó el resultado anterior en `reports/archive/pre-f2-f3-2026-10-24/` y su manifiesto de ocho archivos también verifica.

**Límites que siguen abiertos:** no se hizo auditoría manual con lector de pantalla; no se ejecutó macOS nativo ni Linux con Docker rootless; CI remoto sigue dispensado por el usuario; el DOCX académico aún necesita abrirse en Word/LibreOffice para recalcular y revisar páginas y los datos reales del equipo. No se declara cierre global al 100%. No se creó commit en esta revalidación; HEAD observado `14b2419b3394d985b93d35514c3b800028060d9c` no incluye los cambios locales aquí verificados.

## Cierre del feedback de Fase 1 — 2026-10-23

- Se actualizó `docs/Informe_Investigacion_Pseudo_Studio.docx`: el título de portada ahora identifica el informe; el índice usa referencias dinámicas de página y el documento agrega número de página en el pie; se incorporaron categorías/tipos, reglas léxicas, equivalencias y justificación de Python/JavaScript; las cuatro traducciones manuales A/B incluyen comentarios.
- `examples/phase1-translations/` contiene las cuatro traducciones manuales independientes. El JavaScript de A/B lee una línea por cada Leer usando fs.readSync; no depende de preguntas asíncronas que descartan eventos line cuando stdin llega en un lote.
- `python3.12 scripts/run_phase1_manual_acceptance.py`: **12/12** ejecuciones locales exitosas con Python 3.12.3 y Node.js v22.22.2; los seis datasets A/B se enviaron a cada proceso en una sola escritura de stdin. stdout coincide exactamente con prompts y salida oficial, stderr queda vacío y exit code es 0. Reporte y hashes: `reports/phase1-manual-acceptance.json/.md`.
- Se alineó el lexer con la EBNF: ahora acepta el literal decimal `.5`, además de `3.25`; la prueba de lexer y la ejecución de una fuente con `.5` producen `0.5` tanto en Python como en JavaScript.
- `.venv/bin/pytest -q backend/tests/test_lexer.py backend/tests/test_phase1_manual_translations.py`: **9 pruebas + 12 subtests aprobados**; Ruff y `node --check` pasan en los archivos modificados.
- Suite sin dependencias de OCI: **43 passed, 2 deselected, 33 subtests passed** con pruebas del lexer, parser, semántica, codegen, compilador, proyectos, fixtures y A/B.
- Intento de suite completa: **51 passed, 15 failed, 16 errors, 33 subtests passed**. Los casos que fallan requieren ejecución/estado del runner OCI; `health` informa `degraded` porque Docker no responde y las pruebas de integración reportan `RUN_SANDBOX_UNAVAILABLE`. No se deshabilitaron ni alteraron esas pruebas.
- Las imágenes `reports/phase1-execution-python.png` y `reports/phase1-execution-javascript.png` representan el stdout realmente capturado de A-1 y B-2, con entradas, runtime y exit code; se insertaron como evidencia visual en el informe.
- El DOCX configura referencias de página y número de página como campos de Word que se actualizan al abrir. No se generó un PDF nuevo en esta sesión: no hay Microsoft Word ni LibreOffice/soffice instalado para paginar y renderizar el documento aquí.
- En esta sesión `python3.12 scripts/manage.py verify` y `start` no pueden habilitar OCI: el engine Docker no responde. Por eso las 12 ejecuciones nuevas son en los runtimes locales y no se presentan como prueba de aislamiento. Las ejecuciones OCI oficiales 30/30 del informe anterior se conservan como evidencia histórica, no se atribuyen a esta sesión.

## Revalidación de traducción con programas complejos — 2026-10-16

Se agregó una batería de programas inéditos para someter el mismo compilador a combinaciones mayores de sintaxis, semántica, generación y ejecución. Las fuentes y expectativas viven en `examples/extended/`; no se alteraron los casos oficiales A–E.

- `.venv/bin/pytest -q`: **80 passed, 67 subtests passed**, 90% de cobertura backend, sin fallos ni skips (112,64 s). Queda un warning de deprecación de `starlette.testclient`/`httpx`.
- `python3.12 scripts/run_extended_acceptance.py`: **45/45 checks** en el runner OCI `docker-desktop-vm`, con Python 3.12.14 y Node v22.22.2: 5 compilaciones válidas, 24 ejecuciones válidas (12 entradas/casos en ambos runtimes), 6 diagnósticos negativos con código/fase/span exactos y 10 errores de runtime controlados en ambos runtimes. Evidencia con entradas, stdout/stderr, exit, duración y hashes en `reports/extended-acceptance-results.json/.md`.
- `python3.12 scripts/run_official_acceptance.py`: **30/30** ejecuciones oficiales A–E en OCI después del cambio semántico; salida exacta, stderr vacío y exit 0. Evidencia regenerada en `reports/acceptance-results.json/.md`.
- `.venv/bin/ruff check backend scripts`, `.venv/bin/ruff format --check backend scripts` y `git diff --check`: pasan; 38 archivos con formato verificado.
- La prueba de una función que concatena texto detectó que un parámetro aún desconocido se trataba como número durante el análisis previo a la llamada. Se corrigió la inferencia en `backend/compiler/semantic.py`: `+` restringe a texto el identificador desconocido y rechaza una llamada con argumento numérico (`N06`, `SEM_TYPE_MISMATCH`, línea 3, columna 10). La salida de ambas traducciones ahora pasa en los casos X04.

Para reproducir los nuevos casos: `.venv/bin/pytest -q backend/tests/test_extended_cases.py` y `python3.12 scripts/run_extended_acceptance.py`. El detalle de alcance está en `docs/EXTENDED_TESTING.md`.

## Revalidación del workspace actual — 2026-10-16

Se repitieron las comprobaciones sobre el checkout de trabajo después de revisar Fase 1:

- `python3.12 scripts/manage.py verify`: sandbox disponible en Docker Desktop VM/WSL2; Python 3.12.14 y Node v22.22.2 con UID no privilegiado, seccomp, `NoNewPrivs` y cero capabilities.
- `python3.12 scripts/manage.py smoke`: exit 0; Python y JavaScript devolvieron `OK=42`; API `ready` y frontend HTTP 200.
- `python3.12 scripts/run_official_acceptance.py`: **30/30** ejecuciones OCI reales para A–E, con exit 0, salida exacta y stderr vacío. Reportes regenerados en `reports/acceptance-results.json/.md`.
- `.venv/bin/pytest -q`: **76 passed + 22 subtests**, 90% de cobertura backend; sin fallos. Persiste un warning deprecado de `starlette.testclient` con `httpx`.
- `npm run build`: compilación TypeScript/Vite correcta. `npm run test:e2e`: **6/6**; incluye análisis/traducción, descargas, consola interactiva, proyectos, 30 ejecuciones A–E desde UI, Defensa, navegación por teclado y axe.
- `.venv/bin/ruff check backend scripts` y `.venv/bin/ruff format --check backend scripts`: pasan. Se aplicó el formato Ruff pendiente en `backend/generators/codegen.py` y luego pasó la suite completa.
- `npm audit --audit-level=moderate` desde `frontend/`: cero vulnerabilidades. `pip-audit --strict --no-deps --disable-pip -r requirements.lock`: cero vulnerabilidades conocidas; conserva el aviso de que los pins Python no llevan hashes.
- Se ejecutaron las cuatro traducciones manuales del informe académico con sus seis casos A/B por destino: Python 6/6 en runtime aislado y JavaScript 6/6 mediante entrada interactiva, todos con el resultado oficial.
- El preview actual cargó Pseudo / Studio con `API lista` y `Sandbox verificado`; analizar A mostró 46 tokens y generar produjo Python y JavaScript con el hash vigente.

### Estado editorial de la entrega académica

`docs/Informe_Investigacion_Pseudo_Studio.docx` contiene los objetivos, arquitectura, gramática EBNF, especificación de Python/JavaScript, traducciones manuales A/B, conclusiones y referencias APA 7. Las cuatro traducciones manuales pasan sus casos oficiales. El índice ya usa referencias `PAGEREF` y el pie usa `PAGE`; Word debe recalcular los campos al abrir el DOCX (o con Ctrl+A, F9). No se dispone aquí de un renderizador DOCX/PDF para certificar la paginación final ni para generar el PDF. La portada conserva los espacios de integrantes sin completar porque no se recibieron sus nombres y carnés; no se inventaron datos.

Los gates de accesibilidad manual, CI remota (dispensada anteriormente por el usuario) y prueba nativa en plataformas adicionales siguen como se describen en `docs/REMAINING_GATES.md`; no son parte del resultado 30/30 ni se reportan como cerrados.

## Revalidación automática WSL tras reactivar Docker

El 2026-10-10 se ejecutó `bash scripts/validate_wsl.sh` sobre el commit `5bce0a1808066b9e2a156a4bb2c788a1b4b93f27`, en un clon limpio conservado en `reports/runs/wsl-20261010T175319Z-z0u3ep/workspace`. Las 30 etapas terminaron con exit 0. El resumen reproducible, commit, entorno y 22 hashes de evidencias se guardan en `reports/wsl-validation-summary.json`. Se conservaron los reportes históricos sin contarlos como resultado nuevo.

- Bootstrap desde lockfiles, pre-commit/Ruff y build: pasan.
- Sandbox: Docker 28.1.1 con frontera `docker-desktop-vm`; Python 3.12.14 y Node v22.22.2 pasan controles internos.
- Pytest: **76 passed + 22 subtests**, cero fallos/errores/skips. JUnit cuenta 98 entradas incluyendo subtests; cobertura de líneas de backend **89,82 %** (2240/2494, mostrada redondeada como 90 %). Permanece el warning de deprecación de Starlette TestClient/httpx.
- A–E: **30/30** registros distintos de caso/target, con stdout exacto, stderr vacío, exit 0, inputs, versiones, tiempos y hashes.
- Playwright: **6/6**, un worker, cero retries, servidores propios del clon; axe, teclado, flujos y A–E por UI pasan.
- Arranque/smoke/backup/parada: ambos runtimes imprimen `OK=42`, backup íntegro y puertos 8000/5173 libres al finalizar.
- pip-audit y npm audit: cero vulnerabilidades (JSON revisados). pip-audit recomienda añadir hashes a los paquetes fijados; ese aviso no se ocultó.
- Benchmark, 30 iteraciones: 100 líneas p95 **6,264 ms**; 1.000 líneas p95 **45,297 ms** en el WSL registrado.
- Fuentes intactas tras la suite; `sha256sum -c reports/SHA256SUMS` validó los 12 artefactos del clon. Consulta Docker final sin contenedores `pseudo-studio` restantes.

La guía de ejecución está en `docs/WSL_TEST_PLAN.md`. Los resultados que siguen corresponden a la validación limpia anterior y se conservan como historial.

Después de la suite se arrancó el workspace principal con `python3.12 scripts/manage.py start` y se ejecutó de nuevo `python3.12 scripts/manage.py smoke`: exit 0; Python 3.12.14 y Node v22.22.2 produjeron `OK=42`, con source SHA-256 `5d1e7c922a35ceb4f4d9fa6e344f221f65cd7400c07e67c3251c2b34c708e290`. La salida y los hashes de artefacto están en `reports/wsl-workspace-smoke.json`. Health fue `ready` y la página del frontend respondió HTTP 200. Ambos procesos quedaron activos para la auditoría manual.

Fecha: 2026-10-10. Código de verificación API/runtime y snapshots en `48ced1a`; navegación de teclado y E2E 6/6 en `4aa18fd`; endurecimiento del runner de CI rootless en `2adddeb`. La copia temporal usada para la validación limpia fue `/tmp/pseudo-studio-validation-0o8tswmq/workspace`; se preparó sin `.git`, `.venv`, `node_modules`, `data`, `reports` ni cachés antes del bootstrap. La fuente actual, incluyendo snapshots y matriz de rutas, se sincronizó antes de la suite final.

## Resultado ejecutado

| Capa | Comando / evidencia | Resultado |
|---|---|---|
| Bootstrap limpio | `python3.12 scripts/manage.py bootstrap` | Instala Python lock, frontend con `npm ci`, Chromium Playwright e imágenes OCI fijadas por digest. Exit 0. |
| Controles del runner | `python3.12 scripts/manage.py verify` | Disponible; Docker Desktop VM WSL2; imágenes presentes; UID 10001, cero capabilities, `NoNewPrivs=1`, seccomp activo y ambos runtimes ejecutables. |
| Suite backend limpia | `.venv/bin/pytest -q --cov=backend/app --cov-report=term-missing:skip-covered` | **76 passed, 22 subtests passed**, 90% de cobertura; un warning deprecado de Starlette TestClient (`httpx2`), sin fallos. |
| Lint y formato | `.venv/bin/ruff check backend scripts`; `.venv/bin/ruff format --check backend scripts` | Pasan; 36 archivos verificados. `pre-commit run --all-files` también pasa en checkout Git. |
| UI producción | `npm run build` | TypeScript y Vite pasan; build producido. |
| E2E desde copia limpia | `npm run test:e2e` | **6/6 pasaron**; axe WCAG automatizado en las siete secciones; teclado recorre y activa todas las secciones, comprobando foco, `aria-current` y encabezados; editor, traducción, descargas, consola interactiva y batch, cancelación, pruebas, proyectos, persistencia, defensa, ayuda y viewport móvil. Incluye 30 ejecuciones A–E por UI. |
| Diferencial oficial CLI | `python3.12 scripts/run_official_acceptance.py` | **30/30** ejecuciones OCI Python/Node; inputs, stdout, stderr, status/exit, duración, versión y hashes se guardan en JSON/Markdown. |
| Smoke | `python3.12 scripts/manage.py smoke` | Python `3.12.14` y Node `v22.22.2`; ambos imprimen `OK=42`, exit 0. |
| Dependencias | `pip-audit --strict --no-deps --disable-pip -r requirements.lock`; `npm audit --audit-level=moderate` | 64 paquetes Python y 0 vulnerabilidades; npm 0 vulnerabilidades. JSON de auditoría guardado en `reports/`. |
| Seguridad de ejecución | `backend/tests/test_runner_integration.py`; `manage.py verify` | Red/host filesystem/socket bloqueados; pruebas de input, límites de tiempo/memoria/salida, concurrencia y cancelación; sin privilegios en Python y Node. |
| Rutas HTTP/WS | `docs/API_ROUTE_MATRIX.md`; `backend/tests/test_api.py` | Rutas enumeradas con éxito/error; `run`, `tests/run` y WebSocket devuelven fallo cerrado cuando el sandbox está degradado. |
| Workflow CI | PyYAML parsea `.github/workflows/ci.yml`; `bash -n` a los ocho bloques shell; `apparmor_parser --preprocess` | YAML/shell y preprocesado del perfil pasan. WSL no expone AppArmor para cargarlo. `main` se publicó en el repo público; el usuario dispensó la comprobación remota, por lo que P11-F6 queda sin verificar. |
| Regresión de codegen | `backend/tests/test_codegen_snapshots.py` | Diez snapshots (A–E Python/JavaScript) coinciden con código recién generado; no se usan para simular ejecución. |
| Casos negativos | `docs/NEGATIVE_TEST_MATRIX.md` | N-01..N-12 trazados a diagnóstico, error runtime, límites, aislamiento, timeout y limpieza de sesiones. |

## Aceptación A–E

La instalación limpia generó `reports/clean-install-acceptance-results.json` y `.md`: 30/30 ejecuciones reales, una por cada caso A–E en Python y Node. Cada registro incluye el input oficial, salida esperada/real, `stderr`, estado, código de salida, duración, SHA-256 de fuente y artefacto y versión runtime. El reporte del workspace también está en `reports/acceptance-results.json` y `.md`.

Los tests adicionales ejecutan tres programas inéditos en ambos runtimes, expresiones aritméticas y cadenas con Hypothesis, límites de B y C, errores de arrays 1-based, recursión, `%` negativo, input no confiable y diagnósticos léxicos/sintácticos/semánticos. Las salidas de Python/Node se comparan en crudo y tras normalizar solamente terminadores `CRLF/CR` a `LF`; el reporte conserva el diff crudo.

## Sandbox verificado

- Frontera: Docker Desktop con VM WSL2 identificada; el daemon **no** se presenta como rootless.
- Imágenes Python y Node fijadas por digest en `sandbox/runtime-images.json`.
- Contenedor sin red, root filesystem read-only, usuario no privilegiado, `cap-drop=ALL`, `no-new-privileges`, seccomp, tmpfs efímero.
- Límites verificados: 5 s de pared, 256 MiB, 1 CPU, 64 procesos, 1 MiB stdout/stderr y cuatro ejecuciones concurrentes.
- El API bloquea `run` si fallan los healthchecks o la verificación del aislamiento.

Esta VM equivalente satisface la alternativa de aislamiento aceptada por el requisito funcional. El daemon no es rootless; el runtime se ejecuta dentro de la VM Linux verificada. Las tareas P1-07/P7-02 se verifican por esta alternativa permitida y la limitación del daemon queda declarada.

## Otras mediciones y artefactos

- `reports/compiler-performance.json/.md` conserva el benchmark de 30 iteraciones para 100 y 1.000 líneas, con percentiles y entorno medido.
- `reports/generated/` contiene los 10 artefactos generados por el compilador más sus mapas de origen y manifiesto. Son salida real, no fixtures de ejecución.
- En WSL2, Python 3.12.3 y 12 CPU, el benchmark registró 100 líneas: p50 3.731 ms / p95 5.100 ms; 1.000 líneas: p50 43.960 ms / p95 68.676 ms. 30 iteraciones por tamaño.
- `reports/ui-workbench-clean.png` es captura Playwright de la copia limpia; `reports/clean-install-playwright/` conserva el reporte HTML y el resultado final de Playwright.
- `docs/API_ROUTE_MATRIX.md` da referencias por cada ruta; `docs/NEGATIVE_TEST_MATRIX.md` enlaza cada N-01..N-12 con pruebas ejecutables.
- `reports/clean-install-python-dependency-audit.json` y `reports/clean-install-npm-dependency-audit.json` contienen el resultado de auditoría.

SHA-256 de evidencia limpia:

- Acceptance JSON: `0cf2e62f42a5623aa43c28b08ce0df818a2e94011807ee1fcc0ffc56c6fcab8a`.
- npm audit JSON: `ee3191284f92a07f6cef6debf3de2f2ddd9df71688183f4fcd8ee1bd0f154d28`.
- pip-audit JSON: `2f88642648fc33563be5775168fc09b1c531ff65351d101a3965c67b4c259292`.
- Captura Playwright: `8e33de7287eca91d77a2a833a9d6d854d7ff9929f9211323303ddf7132aee2bb`.

## Límites abiertos

El repo `B-caro/Pseudo-studio` ya está configurado y publicado en `main` (`a472179`). El usuario dispensó ejecutar/verificar el CI remoto; P11-F6 permanece sin verificar. Axe automatizado y teclado/foco pasan, pero se requiere una auditoría manual con lector de pantalla y revisión de contraste (P9-17/P12-12). El fallo de acceso a Docker del intento anterior está resuelto: la nueva corrida WSL completa pasa con Docker Desktop VM. RNF-10 sigue parcial por la cobertura de plataformas; no se probó Linux rootless ni macOS con esta corrida. `Context/` se conserva local y no se subió. El detalle y los pasos pendientes están en `docs/REMAINING_GATES.md`. Las rutas API/WS, casos N-01..N-12, limpieza por desconexión y snapshots tienen evidencia local automatizada. No se declara el proyecto cerrado al 100%.
