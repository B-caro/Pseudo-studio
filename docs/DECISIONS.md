# Decisiones de arquitectura y semántica

Este registro documenta decisiones iniciales de implementación. Una decisión no cierra requisitos por sí sola.

## ADR-001 — Monorepo con compilador Python y frontend TypeScript

- **Estado:** implementada y validada desde copia limpia en WSL2; otras plataformas no se ejecutaron.
- **Decisión:** API y pipeline de compilación en Python 3.12 con FastAPI/Pydantic; cliente local en React + TypeScript + Vite con CodeMirror 6; persistencia SQLite usando `sqlite3` y migraciones versionadas. Los archivos lock fijarán versiones exactas.
- **Motivo:** FastAPI ofrece contratos OpenAPI consumibles; Python permite módulos de compilador claros y comparte lenguaje con las pruebas; SQLite satisface uso local sin servicio externo; CodeMirror se integra con edición y spans.
- **Evidencia:** `pyproject.toml`, `requirements.lock`, `frontend/package-lock.json`, `.github/workflows/ci.yml`, `scripts/manage.py`; bootstrap limpio, tests, build y smoke pasaron. No hay remote Git configurado para lanzar CI remoto.

## ADR-002 — La gramática EBNF y `fase_1.pdf` son fuentes distintas y complementarias

- **Estado:** implementada; aceptación real 30/30 repetida en instalación limpia.
- **Decisión:** la EBNF de la especificación v2 gobierna construcciones extendidas y semántica; el texto literal, el orden y las expresiones de A–E se transcriben desde las páginas 3–5 de `fase_1.pdf`. Las tablas oficiales de entrada/salida se preservan.
- **Motivo:** la gramática v2 formaliza extensiones que no están en la entrega académica; el anexo sigue siendo la autoridad para ejemplos y algoritmos académicos.
- **Evidencia:** fuentes y datasets están en `examples/`; `scripts/run_official_acceptance.py` ejecuta cada caso en los dos OCI. Los reportes `reports/acceptance-results.*` y `reports/clean-install-acceptance-results.*` contienen inputs, stdout/stderr, estado, exit code, duración y hashes; ambos dan 30/30. La transcripción mantiene el texto fuente y las entradas documentadas; no adapta el algoritmo para facilitar las pruebas.

## ADR-003 — Sin ejecución generada en el proceso API ni en el host de desarrollo

- **Estado:** obligatoria por el contrato de seguridad.
- **Decisión:** todos los `run` usarán imágenes runtime aisladas, modo no privilegiado, red desactivada, filesystem raíz de solo lectura, área temporal efímera, capacidades retiradas, límites medibles y cancelación. El API bloquea ejecución si el healthcheck del aislamiento no pasa.
- **Motivo:** el servicio HTTP y el código generado tienen fronteras de confianza distintas.
- **Estado del entorno observado:** Docker Desktop 28.1.1 está integrado con WSL2; el servicio declara `docker-desktop` y kernel `microsoft-standard-WSL2`. El detector también acepta kernel `linuxkit` únicamente cuando el servicio se identifica como Docker Desktop, lo que cubre su VM Linux en macOS; un test de clasificación confirma la regla, pero no sustituye una ejecución de runtime en macOS. Las imágenes runtime están fijadas por digest. La verificación ejecutada dentro de ambas imágenes confirmó UID 10001, cero capabilities, `NoNewPrivs=1` y filtro seccomp activo (`Seccomp=2`).
- **Controles de ejecución:** `--network none`, filesystem raíz read-only, perfil Moby seccomp con SHA-256 fijado, `cap-drop=ALL`, `no-new-privileges`, usuario sin privilegios, tmpfs no ejecutable y límites de CPU, RAM, pids, tiempo, salida y concurrencia. El runner rechaza daemons sin rootless o kernel VM identificable de Docker Desktop (`linuxkit`/WSL2).
- **Evidencia:** `backend/runtime/runner.py`, `sandbox/runtime-images.json`, `sandbox/seccomp/moby-default.json`, `backend/tests/test_runner_integration.py`; `verify_controls()` y ejecuciones reales pasan en el entorno disponible. Esto prueba la VM equivalente, no rootless en esta máquina. El código rechaza ejecución si falla el chequeo.

## ADR-004 — Un solo AST validado alimenta ambos generadores

- **Estado:** aceptada.
- **Decisión:** lexer → parser → semántica → AST tipado validado → generator Python/JavaScript. El generador rechaza cualquier diagnóstico de error. `source_hash`, `artifact_hash`, versión del compilador y source maps acompañan cada artefacto.
- **Motivo:** impide que la interfaz o los ejemplos dicten resultados y permite verificar determinismo y obsolescencia.
- **Evidencia:** `backend/compiler/service.py`, `backend/generators/codegen.py` y pruebas de compilador/codegen/conformidad; analiza fuente inédita, devuelve hashes, genera dos targets desde AST y bloquea traducción con errores. 66 tests y 22 subtests pasan desde checkout limpio.

## ADR-005 — Política numérica y de entrada sigue la especificación operativa

- **Estado:** aceptada.
- **Decisión:** palabras clave insensibles a caso, identificadores sensibles a caso y NFC; doble precisión finita; `Leer` numérico, `LeerTexto` textual, `Escribir` concatena sin separador implícito; índices 1-based; `Para` inclusivo y paso automático según dirección; funciones con firma predeclarada y scopes locales.
- **Motivo:** compatibilidad con A–E y semántica explícita para los casos inéditos.
- **Evidencia:** lexer/parser/semántica y runtime helpers probados; incluye tipos, ámbitos, `%`, lectura numérica/textual, arrays 1-based, iteración inclusiva y tests diferenciales oficiales A–E, además de programas inéditos.

## ADR-006 — Verificación visual y automatización de navegador

- **Estado:** verificada con Playwright Chromium; T3 permite evaluación DOM pero su snapshot falla en el cliente.
- **Decisión:** las interacciones del editor, consola, pruebas, proyectos, defensa, ayuda y descargas se verifican en Chromium real mediante `frontend/e2e/workbench.spec.ts`. T3 preview se usa para la vista compartida y para leer estado DOM.
- **Evidencia:** `preview_status` y `preview_evaluate` confirmaron título, API lista, sandbox verificado, siete pestañas y ausencia de scroll horizontal; `preview_snapshot(includeImage=false)` devolvió `PreviewAutomationExecutionError` del cliente. Playwright ejecutó 5/5 flujos desde copia limpia, incluida accesibilidad axe en siete secciones, y guardó captura real bajo `reports/`.
- **Límite restante:** el snapshot/render de la herramienta T3 es un problema del cliente que no impide la interacción automatizada independiente; se mantiene registrado y no se afirma inspección visual nativa por snapshot.
