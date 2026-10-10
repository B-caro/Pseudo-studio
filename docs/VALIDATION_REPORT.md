# Informe de validación — Pseudo / Studio

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
| Workflow CI | PyYAML parsea `.github/workflows/ci.yml`; `bash -n` a los ocho bloques shell; `apparmor_parser --preprocess` | YAML/shell y preprocesado del perfil pasan. No se pudo cargar/validar el perfil en kernel: WSL no expone interfaz AppArmor. Falta ejecutar en GitHub Actions; no hay remote. |
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

No hay remote Git asociado; GitHub Actions está configurado pero no se ejecutó en un runner remoto. Axe automatizado y teclado/foco pasan, pero se requiere una auditoría manual con lector de pantalla y revisión de contraste (P9-17/P12-12). La CI remota (P11-F6) también requiere un remote/runner asociado. macOS nativo no se ejecutó, por lo que RNF-10 sigue parcial. Los pasos para conseguir evidencia de esos gates están en `docs/REMAINING_GATES.md`. Las rutas API/WS, casos N-01..N-12, limpieza por desconexión y snapshots tienen evidencia local automatizada. No se declara el proyecto cerrado al 100%.
