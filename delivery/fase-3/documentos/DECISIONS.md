# Decisiones de arquitectura y semántica

Este registro documenta decisiones iniciales de implementación. Una decisión no cierra requisitos por sí sola.

## ADR-001 — Monorepo con compilador Python y frontend TypeScript

- **Estado:** implementada y validada desde copia limpia en WSL2; otras plataformas no se ejecutaron.
- **Decisión:** API y pipeline de compilación en Python 3.12 con FastAPI/Pydantic; cliente local en React + TypeScript + Vite con CodeMirror 6; persistencia SQLite usando `sqlite3` y migraciones versionadas. Los archivos lock fijarán versiones exactas.
- **Motivo:** FastAPI ofrece contratos OpenAPI consumibles; Python permite módulos de compilador claros y comparte lenguaje con las pruebas; SQLite satisface uso local sin servicio externo; CodeMirror se integra con edición y spans.
- **Evidencia:** `pyproject.toml`, `requirements.lock`, `frontend/package-lock.json`, `.github/workflows/ci.yml`, `scripts/manage.py`; bootstrap limpio, tests, build y smoke pasaron. El repo ya se publicó en `B-caro/Pseudo-studio`; ejecución CI remota dispensada por el usuario, no se toma como evidencia.

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
- **Evidencia:** `backend/compiler/service.py`, `backend/generators/codegen.py` y pruebas de compilador/codegen/conformidad; analiza fuente inédita, devuelve hashes, genera dos targets desde AST y bloquea traducción con errores. 76 tests y 22 subtests pasan desde checkout limpio; los diez snapshots A–E se comparan contra generación real.

## ADR-005 — Política numérica y de entrada sigue la especificación operativa

- **Estado:** aceptada.
- **Decisión:** palabras clave insensibles a caso, identificadores sensibles a caso y NFC; doble precisión finita; `Leer` numérico, `LeerTexto` textual, `Escribir` concatena sin separador implícito; índices 1-based; `Para` inclusivo y paso automático según dirección; funciones con firma predeclarada y scopes locales.
- **Motivo:** compatibilidad con A–E y semántica explícita para los casos inéditos.
- **Evidencia:** lexer/parser/semántica y runtime helpers probados; incluye tipos, ámbitos, `%`, lectura numérica/textual, arrays 1-based, iteración inclusiva y tests diferenciales oficiales A–E, además de programas inéditos.

## ADR-006 — Verificación visual y automatización de navegador

- **Estado:** verificada con Playwright Chromium; T3 permite evaluación DOM pero su snapshot falla en el cliente.
- **Decisión:** las interacciones del editor, consola, pruebas, proyectos, defensa, ayuda y descargas se verifican en Chromium real mediante `frontend/e2e/workbench.spec.ts`. T3 preview se usa para la vista compartida y para leer estado DOM.
- **Evidencia:** Playwright ejecutó 10/10 pruebas en Chromium, con axe y teclado para ocho secciones, y guardó capturas reales en `reports/`. La interacción no depende de la inspección por snapshot.
- **Límite restante:** el snapshot/render de la herramienta T3 es un problema del cliente que no impide la interacción automatizada independiente; se mantiene registrado y no se afirma inspección visual nativa por snapshot.

## ADR-007 — La desconexión requiere cancelación resistente a la carrera de arranque OCI

- **Estado:** implementada y probada con socket WebSocket real.
- **Decisión:** mantener una sola tarea de recepción WebSocket durante la sesión; cancelar y esperar esa tarea al terminar. La cancelación OCI reintenta `kill` mientras el contenedor puede estar registrándose, con un límite temporal, y comprueba que la sesión se haya liberado.
- **Motivo:** el cliente podía desconectarse después del evento `started` y antes de que el daemon registrara el contenedor; un único `docker kill` temprano podía fallar y dejar el proceso activo.
- **Evidencia:** `test_websocket_disconnect_kills_container_and_releases_session`, `test_interactive_idle_input_expires_and_returns_timeout` y `test_concurrency_quota_rejects_excess_run_and_releases_slot_after_cancel` pasan en la suite limpia.

## ADR-008 — El runner remoto de CI verifica Docker rootless antes de ejecutar

- **Estado:** workflow configurado; ejecución en GitHub Actions pendiente.
- **Decisión:** el job de Ubuntu instala Docker rootless, añade un perfil AppArmor para `rootlesskit` cuando AppArmor está habilitado y exige que `docker info` declare `rootless`. Después ejecuta `manage.py verify` antes de permitir los tests OCI.
- **Motivo:** Ubuntu 24.04 restringe user namespaces no privilegiados bajo AppArmor; el instalador rootless sin paquetes necesita un perfil explícito de `rootlesskit`. La carga falla cerrada si no se confirma el daemon rootless.
- **Evidencia:** `.github/workflows/ci.yml` pasó parse de PyYAML y `bash -n`; Docker documenta el requisito para Ubuntu 24.04 en [Rootless troubleshooting](https://docs.docker.com/engine/security/rootless/troubleshoot/). El workflow se publicó en `B-caro/Pseudo-studio`; el usuario dispensó la verificación remota. P11-F6 queda sin verificar, no completada.

## ADR-009 — La concatenación textual también infiere parámetros de función

- **Estado:** implementada y cubierta por regresión.
- **Decisión:** si una concatenación `+` combina texto con un identificador cuyo tipo aún es desconocido, el análisis semántico infiere que el identificador debe ser texto. Una llamada posterior con argumento numérico se rechaza antes de generar código.
- **Motivo:** las firmas se predeclaran para permitir llamadas adelantadas y recursión; los cuerpos se analizan antes de que algunos tipos de argumentos estén disponibles. La restricción evita falsos errores con funciones textuales y mantiene la comprobación de incompatibilidad.
- **Evidencia:** `backend/compiler/semantic.py`, `backend/tests/test_extended_cases.py` y los casos N06/X04 en `examples/extended/cases.json`; el parámetro textual acepta `LeerTexto` y rechaza un argumento numérico con `SEM_TYPE_MISMATCH`.

## ADR-010 — Python y JavaScript como destinos comparables y ejecutables

- **Estado:** aceptada.
- **Decisión:** los dos destinos se generan desde el mismo AST y se documentan con sus runtimes explícitos: Python 3.12 y JavaScript en Node.js 22. La categoría numérica fuente number incluye literales enteros y decimales; cadenas y booleanos mantienen tipos separados.
- **Motivo:** Python permite presentar traducciones legibles y cercanas a los algoritmos de aula. JavaScript demuestra una segunda sintaxis con operadores, valores y entrada/salida distintos, y Node.js ofrece un runtime autónomo alineado con el ecosistema web de la interfaz. La diferencia pedagógica muestra que la salida proviene de un modelo común y no de reemplazos de texto.
- **Evidencia:** examples/phase1-translations/, backend/tests/test_phase1_manual_translations.py y docs/Informe_Investigacion_Pseudo_Studio.docx. Los seis casos A/B se ejecutan con entradas enviadas juntas a ambos runtimes.

## ADR-011 — Literales numéricos y parámetros arreglo preservan el contrato común

- **Estado:** implementado y equivalencia de ejecución verificada en OCI el 2026-10-24.
- **Decisión:** emitir literales numéricos integrales como flotantes en Python para mantener el tipo de doble precisión de JavaScript. Inferir parámetros usados como arreglos y rechazar argumentos escalares; copiar el arreglo 1D al entrar a la función (`list` en Python, `slice` en JavaScript).
- **Motivo:** Python integers tienen precisión arbitraria y, sin conversión, podían divergir de JavaScript alrededor de `2^53`. Los arreglos son referencias mutables, de modo que pasar el objeto directamente no cumple paso por valor.
- **Evidencia:** `backend/tests/test_codegen.py` prueba las emisiones; `test_semantic.py` comprueba tipo de parámetro, argumento inválido y dimensiones; `test_runner_integration.py` confirma valores cercanos a 2^53, productos grandes y copia de arreglos. Un caso con un producto `1e308 * 10` encontró salida no finita sin diagnóstico; `BaseEmitter.expression` ahora enruta suma/resta/multiplicación numéricas por `__ps_check_number`. `examples/extended/runtime-errors/nonfinite_operation.psc` verifica que Python y Node devuelvan `RUN_NONFINITE` en OCI.

## ADR-012 — Contrato explícito para archivos de texto

- **Estado:** implementación API/UI y pruebas API listas; E2E del navegador se registra por separado.
- **Decisión:** aceptar archivos `.psc` y `.txt` como UTF-8 estricto; quitar un BOM inicial y conservar CRLF/LF. Exportar el artefacto completo vigente de cada destino como `python-txt` y `javascript-txt`, idéntico byte a byte al `.py`/`.js`. Exportar diagnósticos en `diagnostics-txt` con hash, fase, código, ubicación, mensaje y sugerencia.
- **Motivo:** permitir los intercambios solicitados por la rúbrica, mantener las descargas nativas y evitar reemplazos invisibles de bytes que alterarían los spans y hashes.
- **Evidencia:** `backend/tests/test_exports_txt.py` prueba bytes/MIME/archivo inválido/diagnósticos; `frontend/e2e/compiler-exports.spec.ts` y `workbench.spec.ts` recorre controles, archivo BOM/CRLF y errores UTF-8. El build TypeScript se verificó; la corrida E2E final se registra en `VALIDATION_REPORT.md`.

## ADR-013 — Convertir spans Python a offsets UTF-16 en el editor

- **Estado:** implementado; E2E visual pendiente de ejecución en esta revisión.
- **Decisión:** conservar los spans de backend como offsets de puntos de código y convertirlos a longitud UTF-16 antes de seleccionar el rango en CodeMirror.
- **Motivo:** JavaScript y CodeMirror cuentan una letra fuera del plano multilingüe como dos unidades UTF-16; Python la cuenta como un punto de código. Sin conversión, el editor enfocaba una columna anterior.
- **Evidencia:** `frontend/src/main.tsx::focusSpan` y el E2E con `😀` seguido de un identificador faltante prueban que se selecciona el identificador completo.
