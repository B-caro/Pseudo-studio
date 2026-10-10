# Informe de validación — Pseudo / Studio

Fecha: 2026-10-10. La copia temporal usada para la instalación limpia fue `/tmp/pseudo-studio-validation-0o8tswmq/workspace`; excluyó `.git`, `.venv`, `node_modules`, `data`, `reports` y archivos de caché antes del bootstrap. El código fuente copiado incluye la implementación y los tests actuales.

## Resultado ejecutado

| Capa | Comando / evidencia | Resultado |
|---|---|---|
| Bootstrap limpio | `python3.12 scripts/manage.py bootstrap` | Instala Python lock, frontend con `npm ci`, Chromium Playwright e imágenes OCI fijadas por digest. Exit 0. |
| Controles del runner | `python3.12 scripts/manage.py verify` | Disponible; Docker Desktop VM WSL2; imágenes presentes; UID 10001, cero capabilities, `NoNewPrivs=1`, seccomp activo y ambos runtimes ejecutables. |
| Suite backend | `.venv/bin/pytest -q --cov=backend/app --cov-report=term-missing:skip-covered` | **66 passed, 22 subtests passed**, 88% de cobertura; 1 warning deprecado de Starlette TestClient (`httpx2`), sin fallos. |
| Lint y formato | `.venv/bin/ruff check backend scripts`; `.venv/bin/ruff format --check backend scripts` | Pasan; 34 archivos ya formateados. |
| UI producción | `npm run build` | TypeScript y Vite pasan; build producido. |
| E2E desde copia limpia | `npm run test:e2e` | **5/5 pasaron**; axe WCAG automatizado en las siete secciones, keyboard focus, editor, traducción, descargas, consola interactiva y batch, cancelación, pruebas, proyectos, persistencia, defensa, ayuda y viewport móvil. Incluye 30 ejecuciones A–E por UI. |
| Diferencial oficial CLI | `python3.12 scripts/run_official_acceptance.py` | **30/30** ejecuciones OCI Python/Node; inputs, stdout, stderr, status/exit, duración, versión y hashes se guardan en JSON/Markdown. |
| Smoke | `python3.12 scripts/manage.py smoke` | Python `3.12.14` y Node `v22.22.2`; ambos imprimen `OK=42`, exit 0. |
| Dependencias | `pip-audit --strict --no-deps --disable-pip -r requirements.lock`; `npm audit --audit-level=moderate` | 64 paquetes Python y 0 vulnerabilidades; npm 0 vulnerabilidades. JSON de auditoría guardado en `reports/`. |
| Seguridad de ejecución | `backend/tests/test_runner_integration.py`; `manage.py verify` | Red/host filesystem/socket bloqueados; pruebas de input, límites de tiempo/memoria/salida, concurrencia y cancelación; sin privilegios en Python y Node. |

## Aceptación A–E

La instalación limpia generó `reports/clean-install-acceptance-results.json` y `.md`: 30/30 ejecuciones reales, una por cada caso A–E en Python y Node. Cada registro incluye el input oficial, salida esperada/real, `stderr`, estado, código de salida, duración, SHA-256 de fuente y artefacto y versión runtime. El reporte del workspace también está en `reports/acceptance-results.json` y `.md`.

Los tests adicionales ejecutan tres programas inéditos en ambos runtimes, expresiones aritméticas y cadenas con Hypothesis, límites de B y C, errores de arrays 1-based, recursión, `%` negativo, input no confiable y diagnósticos léxicos/sintácticos/semánticos. Las salidas de Python/Node se comparan en crudo y tras normalizar solamente terminadores `CRLF/CR` a `LF`; el reporte conserva el diff crudo.

## Sandbox verificado

- Frontera: Docker Desktop con VM WSL2 identificada; el daemon **no** se presenta como rootless.
- Imágenes Python y Node fijadas por digest en `sandbox/runtime-images.json`.
- Contenedor sin red, root filesystem read-only, usuario no privilegiado, `cap-drop=ALL`, `no-new-privileges`, seccomp, tmpfs efímero.
- Límites verificados: 5 s de pared, 256 MiB, 1 CPU, 64 procesos, 1 MiB stdout/stderr y cuatro ejecuciones concurrentes.
- El API bloquea `run` si fallan los healthchecks o la verificación del aislamiento.

Esta VM equivalente satisface la alternativa de aislamiento aceptada por el requisito funcional. Queda sin instalar/probar un engine rootless explícito en este entorno; P1-07/P7-02 permanecen abiertos en la tabla operacional porque el plan los formula así.

## Otras mediciones y artefactos

- `reports/compiler-performance.json/.md` conserva el benchmark de 30 iteraciones para 100 y 1.000 líneas, con percentiles y entorno medido.
- `reports/generated/` contiene los 10 artefactos generados por el compilador más sus mapas de origen y manifiesto. Son salida real, no fixtures de ejecución.
- En WSL2, Python 3.12.3 y 12 CPU, el benchmark registró 100 líneas: p50 3.731 ms / p95 5.100 ms; 1.000 líneas: p50 43.960 ms / p95 68.676 ms. 30 iteraciones por tamaño.
- `reports/ui-workbench-clean.png` es captura Playwright de la copia limpia; `reports/clean-install-playwright/` conserva el reporte HTML y el resultado final de Playwright.
- `reports/clean-install-python-dependency-audit.json` y `reports/clean-install-npm-dependency-audit.json` contienen el resultado de auditoría.

## Límites abiertos

No hay remote Git asociado; GitHub Actions está configurado pero no se ejecutó en un runner remoto. La integración runtime comprobada es WSL2; macOS nativo y Linux con engine rootless siguen sin probar. Axe automatizado y teclado/foco pasaron, pero no se hizo auditoría manual con lector de pantalla. También quedan los casos negativos N-01..N-12 completos, la limpieza por desconexión/expiración de sesiones y una batería negativa/positiva de cada ruta API/WS. Esos pendientes aparecen sin marcar en `docs/IMPLEMENTATION_STATUS.md`; no se declara el proyecto cerrado al 100%.
