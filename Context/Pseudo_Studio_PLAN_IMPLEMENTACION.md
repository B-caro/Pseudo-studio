# PSEUDO / STUDIO — PLAN MAESTRO DE IMPLEMENTACIÓN

**Versión:** 2.0\
**Documento rector:** `Pseudo_Studio_Requerimientos_v2_Operativo.pdf`\
**Objetivo:** construir, integrar y verificar el sistema completo; prohibidos mocks de funcionalidad, código que únicamente imite resultados, controles inertes y declaraciones de éxito no verificadas.\
**Estado inicial:** ninguna tarea se presupone completada. El equipo de implementación deberá inspeccionar el repositorio para determinar el estado real y verificarlo antes de marcar cualquier casilla.

## Cómo ejecutar este plan

1. Leer el PDF rector completo, este plan y los PDF académicos A–E si están disponibles. La especificación v2.0 es el contrato técnico; el anexo `fase_1.pdf` prevalece para el texto y salida oficiales de A–E.
2. Crear `docs/IMPLEMENTATION_STATUS.md` y un inventario de archivos, versiones, servicios y dependencias existentes; no sobrescribir trabajo válido.
3. Desarrollar en el orden indicado, con tareas técnicamente independientes en paralelo solo si no producen conflictos. No confundir **orden de construcción** con exclusión de alcance.
4. Cada checkbox `[ ]` se convierte en `[x]` únicamente después de verificar en el repositorio una implementación real, una prueba que pasó y evidencia. Anotar commit, ruta de test/comando, fecha y resultado en `docs/IMPLEMENTATION_STATUS.md`.
5. Nunca afirmar «100 % completo» mientras una prueba de integración, sandbox o requisito esté pendiente. Registrar bloqueadores concretos con instrucciones precisas para desbloquearlos, continuar todo lo independiente y reintentar lo bloqueado.
6. **Bucle operacional:** seleccionar próxima tarea libre de dependencias → implementar código productivo → añadir tests → ejecutar pruebas → diagnosticar/regresar a corregir → verificar GUI/API/runtime cuando aplique → actualizar checkbox/evidencia → crear commit pequeño → seguir con la siguiente tarea.
7. Ejecutar la **suite integral** después de cada hito de integración y otra vez tras cambios de codegen, gramática, runners, interfaces o protocolos.
8. Al concluir, entregar informe final de trazabilidad RF-01..RF-29, RNF-01..RNF-12, resultados A–E por destino y caso, instalación limpia, riesgos y comandos de reproducción.

> **Definición de «completado»:** existe implementación conectada de extremo a extremo, pruebas automatizadas que han pasado y evidencia reproducible. Una UI bonita, tests con datos prefijados o código sin ejecutarse no cierran tareas. No desactivar/alterar pruebas para conseguir verde ni insertar comportamientos condicionales por el nombre del ejemplo.

## Dependencias del camino crítico

`P0 diagnóstico → P1 arquitectura/entorno → P2 contratos/gramática → P3 lexer → P4 parser/AST → P5 semántica → P6 generadores PY y JS → P7 aislamiento/ejecución → P8 API integración → P9 UI real → P10 proyectos/exports → P11 pruebas A–E e inéditas → P12 seguridad/calidad → P13 aceptación/release`.

**Paralelizables después de P2:** vista UI con contracts, persistencia, documentación, scaffolding de casos; **no** se declaran integradas hasta P8/P9. Se pueden realizar pruebas tempranas tan pronto exista el módulo correspondiente.

---

## P0 — Reconocimiento del repositorio y preparación de pruebas

- [ ] P0-01 — Verificar directorio de trabajo, estado de Git, ramas, archivos locales y dependencias existentes; evitar pérdida de datos.
- [ ] P0-02 — Leer íntegramente PDF rector y anexos académicos; generar tabla de correspondencia entre RF/RNF y entregables.
- [ ] P0-03 — Identificar proyecto previo funcional, si existe; conservar componentes correctos y marcar gaps sustentados por tests.
- [ ] P0-04 — Establecer y documentar sistema operativo, CPU, memoria y permisos disponibles; verificar Python, Node, gestor OCI rootless, Git y navegadores.
- [ ] P0-05 — Crear `docs/IMPLEMENTATION_STATUS.md` con tabla `ID | estado | componente | test | evidencia | commit | bloqueo`.
- [ ] P0-06 — Crear `docs/DECISIONS.md` y registrar decisiones de compatibilidad, seguridad, semántica y convenciones.
- [ ] P0-07 — Reproducir desde `fase_1.pdf` los programas A–E sin cambiar su lógica; registrar en fixtures fuente y tres datasets oficiales.
- [ ] P0-08 — Crear matriz de aceptación `docs/TRACEABILITY.md`: RF-01..29, RNF-01..12, tests previstos, capa de UI y API.
- [ ] P0-09 — Establecer línea base de ejecución: comandos disponibles, tests existentes, errores reales y próximos pasos.

**Salida de hito:** repositorio inventariado, alcance sin omisiones y línea base reproducible.

## P1 — Estructura real, entorno y ciclo de desarrollo

- [ ] P1-01 — Estructurar monorepo frontend/backend/docs/examples/sandbox/scripts con separación de responsabilidades.
- [ ] P1-02 — Inicializar backend Python moderno, gestor de paquetes/lockfile y `pyproject.toml` con Ruff, mypy/pyright si procede y pytest.
- [ ] P1-03 — Inicializar frontend TypeScript, Vite, framework visual y editor CodeMirror/Monaco; lockfile reproducible.
- [ ] P1-04 — Definir soporte del servidor API FastAPI y tipado estricto de contratos Pydantic.
- [ ] P1-05 — Configurar SQLite, esquema inicial de proyectos, mecanismo de migraciones y almacenamiento de artefactos efímeros.
- [ ] P1-06 — Añadir `.env.example`, configuración de loopback, niveles de logging, CORS/origin y cuotas configurables.
- [ ] P1-07 — Preparar runner OCI rootless (Podman o Docker rootless) con imágenes dedicadas para Python y Node, versiones fijadas.
- [ ] P1-08 — Crear scripts `bootstrap`, `start`, `stop`, `verify`, `smoke` compatibles con entorno disponible; documentar Windows/macOS/Linux.
- [ ] P1-09 — Añadir pre-commit/formato, lint y test runner; CI inicial de instalación y pruebas mínimas.
- [ ] P1-10 — Validar desde clon limpio o directorio temporal que instalaciones e imports funcionan.
- [ ] P1-11 — Registrar en `README.md` prerequisitos, comandos exactos, puertos, formas de operar y solución de fallos típicos.

**Prueba de salida:** backend y frontend arrancan con healthcheck inicial, dependencias bloqueadas y suite de arranque reproducible.

## P2 — Contrato semántico, gramática y datos

- [ ] P2-01 — Crear `docs/gramatica.ebnf` a partir de sección 4.2, con reservadas, final de línea, bloques y fuentes A–E.
- [ ] P2-02 — Definir convenciones de nombres Unicode/case, palabras reservadas, strings, escapes, números y comentarios.
- [ ] P2-03 — Formalizar precedencia de operadores, llamadas, índice, comparaciones, `Y/O/No`, cortocircuito y paréntesis.
- [ ] P2-04 — Formalizar `Leer` numérico, `LeerTexto` textual, `Escribir` sin separador implícito, errores de input y formato numérico equivalente.
- [ ] P2-05 — Definir `Para` inclusivo, `Paso`, descenso, límites, `Mientras` y semántica de control.
- [ ] P2-06 — Formalizar `Dimension` e indexación 1-based; inicialización y límites de arrays.
- [ ] P2-07 — Formalizar `Funcion retorno = Nombre(...)`, variante simple, ámbitos, predeclaración, recursion y retorno.
- [ ] P2-08 — Definir tipos, coerciones prohibidas/aceptadas, bool, `%` negativo, división y normalización de salida.
- [ ] P2-09 — Crear modelos y schemas de token, span, AST, symbols, diagnostic, source map, compile result y run result.
- [ ] P2-10 — Crear contrato de eventos WebSocket y payload de ejecución por lotes; estados y códigos de error.
- [ ] P2-11 — Establecer test fixtures de conformidad por producción gramatical, incluyendo terminadores faltantes y anidación.
- [ ] P2-12 — Definir contratos de independencia de scripts: ejecución autónoma con helper embebido o empaquetado.
- [ ] P2-13 — Revisar formalmente que los cinco programas académicos son aceptados por la gramática diseñada.

**Salida de hito:** una fuente de verdad formal y contratos consumibles por motor, UI, API, runner y tests.

## P3 — Lexer real (RF-03, RF-07)

- [ ] P3-01 — Implementar lexer por estados/transiciones, no mapeos de resultados de ejemplos.
- [ ] P3-02 — Reconocer reservadas/identificadores con política de case y Unicode documentada.
- [ ] P3-03 — Reconocer literales numéricos enteros y decimales, sin aceptar NaN/Infinity por entrada léxica.
- [ ] P3-04 — Implementar cadenas con escapes y diagnósticos de escape/comilla inválidos.
- [ ] P3-05 — Reconocer operadores compuestos antes de simples y símbolos de arrays, llamadas y paréntesis.
- [ ] P3-06 — Emitir tokens `NEWLINE` conservando la semántica de línea y ubicaciones exactas.
- [ ] P3-07 — Procesar comentarios y espacios sin destruir posiciones del código fuente.
- [ ] P3-08 — Emitir diagnósticos estructurados de caracteres, números o strings inválidos, sin excepciones no gestionadas.
- [ ] P3-09 — Crear unit tests de límites, Unicode, strings, tokens compuestos y errores recuperables.
- [ ] P3-10 — Validar tokenización real de A–E y un programa nuevo, comparando offsets y ubicaciones.

**Salida de hito:** `lexer(source)` retorna tokens y diagnósticos reales con test de regresión.

## P4 — Parser y AST navegable (RF-04, RF-11, RF-15 a RF-17, RF-28)

- [ ] P4-01 — Implementar parser recursivo/Pratt con consumo inequívoco de fin de línea.
- [ ] P4-02 — Implementar nodos AST tipados con source spans y serialización JSON segura.
- [ ] P4-03 — Parsear `Inicio/Fin`, `Leer`, `LeerTexto`, `Escribir`, asignación, expresiones y llamadas.
- [ ] P4-04 — Parsear precedencia, paréntesis, operaciones unarias/bool, comparaciones y `Y/O/No`.
- [ ] P4-05 — Parsear `Si/Entonces/Sino/FinSi` con varios niveles de anidación.
- [ ] P4-06 — Parsear `Para` con `Hasta`, `Paso` opcional y `FinPara`; preservar expresiones de límites.
- [ ] P4-07 — Parsear `Mientras/Hacer/FinMientras` y expresiones booleanas.
- [ ] P4-08 — Parsear `Dimension a[n]`, lecturas, escrituras y asignaciones `a[i] = ...`.
- [ ] P4-09 — Parsear firma con alias de retorno `Funcion area = CalcularArea(...)`, variante simple, `Retornar` y `FinFuncion`.
- [ ] P4-10 — Resolver llamada vs índice por lookahead; aceptar llamadas anidadas y argumentos expresivos.
- [ ] P4-11 — Implementar recuperación de error y cerrar bloques de forma segura, con mensajes y spans.
- [ ] P4-12 — Implementar tests de precedencia, ambigüedad, anidación, bloques vacíos, terminadores faltantes.
- [ ] P4-13 — Obtener AST válido de A–E sin transformar la lógica del programa docente.
- [ ] P4-14 — Probar serialización JSON del AST, nodo → línea origen y navegación hacia tokens.

**Salida de hito:** parser real y AST fiel, capaz de representar A–E y extensiones con errores localizados.

## P5 — Analizador semántico y tabla de símbolos (RF-05 a RF-08)

- [ ] P5-01 — Implementar ámbitos global/local, tabla de símbolos y puntos de definición/referencia.
- [ ] P5-02 — Predeclarar firmas de funciones y resolver invocaciones adelantadas y recursivas.
- [ ] P5-03 — Detectar variables desconocidas, accesos antes de inicializar y referencias fuera de ámbito.
- [ ] P5-04 — Inferir/comprobar número, booleano, string, array y retorno de función.
- [ ] P5-05 — Validar compatibilidad en aritmética, `%`, relación, booleanos y concatenaciones permitidas.
- [ ] P5-06 — Comprobar definición e inicialización de variables por rutas de `Si`/`Sino`; evitar falsos positivos.
- [ ] P5-07 — Validar tipos enteros/positivos para `Dimension`, `Para` y acceso indexado.
- [ ] P5-08 — Detectar usos incorrectos de arrays, índices no enteros y mutaciones inválidas.
- [ ] P5-09 — Validar parámetros, aridad, redeclaraciones, retornos faltantes, `Retornar` fuera de función.
- [ ] P5-10 — Clasificar errores semánticos y ubicar spans exactos en fuente.
- [ ] P5-11 — Determinar estado `traducible` exclusivamente con cero errores en todas las fases.
- [ ] P5-12 — Exponer tabla real de símbolos por ámbito con lecturas/escrituras e inicialización.
- [ ] P5-13 — Probar semántica de A–E, casos inválidos y rutas condicionadas con suites separadas.

**Salida de hito:** análisis y bloqueos reales, símbolos reales y cero artefactos emitidos en fuentes inválidas.

## P6 — Dos generadores reales, interoperables (RF-02, RF-09, RF-10, RF-20)

- [ ] P6-01 — Definir interfaz común `generate(validated_ast, target)`; rechazar AST no validado.
- [ ] P6-02 — Implementar escape correcto de literales y nombres de variables en Python y JavaScript.
- [ ] P6-03 — Emitir declaraciones/asignaciones, llamadas, operaciones y precedencia preservadas.
- [ ] P6-04 — Emitir condicionales anidados y operadores booleanos con cortocircuito.
- [ ] P6-05 — Emitir `Para` inclusivo creciente/decreciente con `Paso`, `Mientras` y acumuladores.
- [ ] P6-06 — Emitir arreglos `Dimension` y todas las operaciones con indexación 1-based y comprobación de rango.
- [ ] P6-07 — Emitir funciones con parámetros, retorno, llamadas anidadas y recursión controlada.
- [ ] P6-08 — Implementar helper runtime Python para `Leer`, `LeerTexto`, `Escribir`, formateo y errores normalizados.
- [ ] P6-09 — Implementar helper runtime Node.js real para `Leer`, `LeerTexto`, `Escribir`, formateo y errores normalizados.
- [ ] P6-10 — Resolver coherencia numérica y diferencias `%`, división y presentación `2` vs `2.0`.
- [ ] P6-11 — Generar código legible con indentación correcta, extensiones .py/.js y source maps.
- [ ] P6-12 — Incluir helpers dentro del archivo exportado o empaquetarlos de forma autónoma documentada.
- [ ] P6-13 — Probar sintaxis de código generado (`python -m py_compile` y `node --check`) dentro del entorno apropiado.
- [ ] P6-14 — Crear snapshots de código y comparación semántica, sin usar snapshots para simular ejecuciones.
- [ ] P6-15 — Verificar que modificar el pseudocódigo modifica la salida del generador cuando corresponda y actualiza hashes.
- [ ] P6-16 — Compilar A–E en ambos destinos y validar que cada archivo pueda iniciarse fuera de la interfaz.

**Salida de hito:** 10 programas generados reales (5×2) con ejecutables independientes del backend en cuanto a lógica.

## P7 — Ejecutor aislado real: batch y consola interactiva (RF-12, RF-21, RF-22, RF-29)

- [ ] P7-01 — Preparar dos imágenes OCI con Python y Node reales, versiones fijadas por digest y usuario sin privilegios.
- [ ] P7-02 — Configurar engine rootless y comprobar explícitamente su operación en el entorno de desarrollo.
- [ ] P7-03 — Implementar runner que escribe artifacts en directorio efímero y ejecuta procesos sin `shell=True`.
- [ ] P7-04 — Deshabilitar red de contenedor; aplicar root fs read-only, tmpfs, cap-drop, no-new-privileges y seccomp.
- [ ] P7-05 — Aplicar límites reales de memoria, tiempo de pared, CPU, número de procesos y bytes stdout/stderr.
- [ ] P7-06 — Separar las sesiones; no montar host/home/secrets/engine socket en contenedores.
- [ ] P7-07 — Enviar inputs por stdin al proceso real, conservando orden de solicitudes `Leer`.
- [ ] P7-08 — Capturar stdout/stderr reales, exit code, duration, timeout/oom y tipo de runtime.
- [ ] P7-09 — Normalizar errores runtime y relacionarlos con source maps sin ocultar stderr técnico de diagnóstico.
- [ ] P7-10 — Implementar `POST /run` batch, con mismas rutas ejecutivas que usa el modo interactivo.
- [ ] P7-11 — Implementar broker de WebSocket, `input_requested`, entrega de respuesta del usuario y streaming stdout/stderr.
- [ ] P7-12 — Implementar cancelación efectiva: terminar proceso/contenedor y liberar archivos/sesiones.
- [ ] P7-13 — Manejar desconexión de cliente, expiración por inactividad, concurrencia y cleanup de sesiones huérfanas.
- [ ] P7-14 — Ejecutar un `.py` trivial y un `.js` trivial con entradas; verificar salida capturada contra la consola del intérprete.
- [ ] P7-15 — Probar división por cero y input inválido; diferenciar compilación exitosa de ejecución fallida.
- [ ] P7-16 — Probar bucle infinito/timeout, mucha salida, OOM, red bloqueada, rutas host inaccesibles y sesiones concurrentes.
- [ ] P7-17 — Implementar healthcheck de engine, imágenes y runtimes que controla disponibilidad del botón Ejecutar.
- [ ] P7-18 — Definir mensaje de bloqueo real si no hay sandbox: no ejecutar sin aislamiento y no mostrar salida ficticia.

**Salida de hito:** pruebas de ejecución real Python/Node con límites y consola interactiva verificadas de extremo a extremo.

## P8 — API real y sincronización interna (RF-08, RF-13, RF-27)

- [ ] P8-01 — Montar FastAPI con routers `/api/v1`, Pydantic, OpenAPI y respuesta de error coherente.
- [ ] P8-02 — Implementar `/analyze` conectado a lexer/parser/semántica/símbolos/diagnósticos auténticos.
- [ ] P8-03 — Implementar `/translate` conectado a AST validado y dos codegens reales; comprobar hashes.
- [ ] P8-04 — Implementar `/run` conectado exclusivamente al runner de P7, sin ejecución del código en el proceso web.
- [ ] P8-05 — Implementar WebSocket de ejecución interactiva con origen permitido y protocolo tipado.
- [ ] P8-06 — Implementar `/examples` alimentado por fixtures A–E persistidos en disco.
- [ ] P8-07 — Implementar `/tests/run` con ejecuciones reales y comparación de ambas salidas.
- [ ] P8-08 — Implementar endpoints CRUD de proyectos y exportaciones con protección de rutas.
- [ ] P8-09 — Implementar `/health` con estado técnico granular y códigos HTTP correctos.
- [ ] P8-10 — Incorporar timeout API, límites de tamaño/requests, validación de inputs y controles CORS/CSRF/origin locales.
- [ ] P8-11 — Incorporar request_id, errores auditables y logs sin imprimir secretos o inputs salvo permiso.
- [ ] P8-12 — Probar cada ruta HTTP/WS con casos positivos, negativos y fallos del sandbox.
- [ ] P8-13 — Bloquear ejecución de artefacto desactualizado cuando difiere `source_hash`.

**Salida de hito:** API completamente operativa que expone servicios reales al navegador y a clientes API externos locales.

## P9 — Experiencia visual funcional de punta a punta (RF-01, RF-02, RF-06, RF-07, RF-12, RF-13, RF-20, RF-26)

- [ ] P9-01 — Implementar diseño responsivo Pseudo / Studio con estados de carga/errores vacíos y accesibilidad básica.
- [ ] P9-02 — Integrar editor real con resaltado de keywords, número de línea, deshacer/rehacer, abrir y guardar.
- [ ] P9-03 — Conectar `Analizar` a `/analyze`, mostrar fase y hash recibidos, no calcular textos ficticios.
- [ ] P9-04 — Panel de tokens con lexema, clase, línea y columna; click enfoca el código.
- [ ] P9-05 — Inspector AST jerárquico y fuente seleccionable; debe renderizar nodos serializados reales.
- [ ] P9-06 — Tabla de símbolos con ámbitos/tipos/inicialización/referencias reales.
- [ ] P9-07 — Lista de errores agrupada por fase, código/posición/hint, marcadores en editor y navegación.
- [ ] P9-08 — Conectar `Traducir` a ambos generadores; actualizar vista Python/JS con código real.
- [ ] P9-09 — Implementar comparador side-by-side, copy, download, source map y marcado de versión.
- [ ] P9-10 — Conectar `Ejecutar Python` y `Ejecutar JavaScript` al sandbox real y mostrar stdout, stderr, tiempo y exit code.
- [ ] P9-11 — Implementar consola interactiva WebSocket con input cuando el proceso lo pide y streaming fiel.
- [ ] P9-12 — Implementar detener/cancelar que aborta proceso real y deja UI consistente.
- [ ] P9-13 — Deshabilitar botones imposibles en caso de validación fallida, fuente desactualizada o sandbox no listo.
- [ ] P9-14 — Guardado automático con indicador de sincronización y advertencia antes de perder cambios.
- [ ] P9-15 — Panel de casos académicos y pruebas propias editable: ejecutar, ver expected/actual/diff y guardar evidencias.
- [ ] P9-16 — Crear modo defensa que llame servicios reales para casos válidos y errores, sin hardcode de resultados.
- [ ] P9-17 — Accesibilidad: teclado, tab order, focus, screenreader/ARIA, contraste, estado no basado solo en color.
- [ ] P9-18 — Probar en navegador real que se editan fuentes inéditas y cambian tokens, AST, codegen y resultados observables.
- [ ] P9-19 — Ejecutar Playwright de los principales flujos, errores, consola, descarga, persistencia y cancelación.

**Salida de hito:** interfaz visual plenamente interconectada con backend, compilador, runtimes y almacenamiento.

## P10 — Gestión de proyectos, exportación y documentación (RF-14, RF-19, RF-24, RF-25)

- [ ] P10-01 — Crear migraciones SQLite y CRUD transaccional de proyecto con validación, IDs y timestamps.
- [ ] P10-02 — Implementar crear/duplicar/renombrar/abrir/guardar/eliminar con confirmación y errores operativos.
- [ ] P10-03 — Implementar control de versión de edición para evitar pisar cambios; conflictos visibles.
- [ ] P10-04 — Persistir/restaurar borradores y estado de sesión; controlar qué datos de input se conservan.
- [ ] P10-05 — Crear módulo de exportación `.psc`, `.py`, `.js`, AST `.json`, símbolos/diagnósticos e informes de prueba JSON, Markdown y PDF obligatorios, con pruebas de apertura/descarga.
- [ ] P10-06 — Verificar MIME, nombres de archivo, escape de rutas y ausencia de traversal en export.
- [ ] P10-07 — Implementar descarga de ambos destinos con helper autocontenido y prueba de ejecución fuera del editor.
- [ ] P10-08 — Incorporar `docs/gramatica.ebnf`/manual de usuario y ayuda contextual dentro de la UI.
- [ ] P10-09 — Documentar datos persistentes, backups, migraciones y restauración del repositorio.
- [ ] P10-10 — Test e2e guardar → cerrar navegador → abrir → recuperar fuente → analizar → ejecutar → exportar.

**Salida de hito:** archivos, datos y resultados quedan persistentes y exportables, no solamente visibles en memoria.

## P11 — Validación exhaustiva con pruebas oficiales, inéditas y diferenciales (RF-18, RF-23)

### A: operaciones y precedencia
- [ ] P11-A1 — A/1: inputs `4,2,3` → `El resultado es: 16` tanto PY como JS.
- [ ] P11-A2 — A/2: inputs `10,5,2` → `El resultado es: 28` en ambos.
- [ ] P11-A3 — A/3: inputs `6,3,4` → `El resultado es: 34` en ambos.
- [ ] P11-A4 — A/negativo: `b=0` no aborta la API; produce `RUN_DIV_ZERO` en ambos.

### B: condiciones anidadas
- [ ] P11-B1 — B/1: `8,80` → `Aprobado` en ambos.
- [ ] P11-B2 — B/2: `7,60` → `Reprobado por asistencia` en ambos.
- [ ] P11-B3 — B/3: `4,90` → `Reprobado por nota` en ambos.
- [ ] P11-B4 — B/bordes: nota `6`, asistencia `75` → aprobado; nota `6`, asistencia `74` → por asistencia.

### C: bucles y acumuladores
- [ ] P11-C1 — C/1: `4` → factorial `24`, suma `20` en ambos.
- [ ] P11-C2 — C/2: `5` → factorial `120`, suma `30` en ambos.
- [ ] P11-C3 — C/3: `1` → factorial `1`, suma `2` en ambos.
- [ ] P11-C4 — Validar for inclusivo y comportamiento del límite `n=0` documentado por el lenguaje/ejemplo.

### D: arreglos
- [ ] P11-D1 — D/1: `3;4,9,2` → promedio `5`, mayor `9` en ambos.
- [ ] P11-D2 — D/2: `4;10,20,5,15` → promedio `12.5`, mayor `20` en ambos.
- [ ] P11-D3 — D/3: `5;1,1,1,1,1` → promedio `1`, mayor `1` en ambos.
- [ ] P11-D4 — Verificar índices 1..n, `a[0]`/`a[n+1]` con error runtime y `Dimension` inválido.

### E: funciones
- [ ] P11-E1 — E/1: `5,4` → área `20`, clasificación `Pequeña` en ambos.
- [ ] P11-E2 — E/2: `10,8` → área `80`, clasificación `Grande` en ambos.
- [ ] P11-E3 — E/3: `6,9` → área `54`, clasificación `Grande` en ambos.
- [ ] P11-E4 — Probar scopes/parametrización, alias retorno, funciones encadenadas y recursión con casos inéditos.

### Casos nuevos y negativos
- [ ] P11-F1 — Crear 3 programas inéditos válidos que usen combinación de operadores, `Mientras`, funciones, arrays y `%` negativo.
- [ ] P11-F2 — Crear 3 programas inéditos inválidos en fases léxica, sintáctica y semántica.
- [ ] P11-F3 — Ejecutar suite negativa `N-01..N-12` de PDF: diagnósticos, runtime, timeout, aislamiento y concurrencia.
- [ ] P11-F4 — Implementar comparador crudo y normalizado de stdout/stderr Python vs Node, sin esconder salidas divergentes.
- [ ] P11-F5 — Crear tests property-based de expresiones/precedencia, cadenas y tipado para detectar divergencias entre destinos.
- [ ] P11-F6 — Comprobar que las mismas pruebas funcionen al ejecutarse desde UI, API, CLI y CI (misma lógica de negocio).
- [ ] P11-F7 — Generar `reports/acceptance-results.json` y `reports/acceptance-results.md` con detalle de entradas, expected, actual, exit code, duración y hash.
- [ ] P11-F8 — Comprobar explícitamente 30/30 ejecuciones oficiales reales exitosas y 0 regresiones obligatorias antes de aprobar hito.

**Salida de hito:** 15 casos × 2 destinos probados, más pruebas negativas e inéditas y evidencias por cada ejecución.

## P12 — Seguridad, fiabilidad, rendimiento, accesibilidad y calidad (RNF-01..12)

- [ ] P12-01 — Probar bloqueo de traducción por errores y no ejecución de artefactos viejos.
- [ ] P12-02 — Probar generación robusta ante inyección en strings/nombres y escaping por destino.
- [ ] P12-03 — Probar patología de parser: anidación profunda, input largo, tokens inválidos y no loop infinito de recuperación.
- [ ] P12-04 — Probar sandbox sin red, host files, home, secretos, sockets, shell arbitraria ni elevación.
- [ ] P12-05 — Probar timeout/OOM/concurrencia/salida masiva, limpieza tras cancelar y sesiones huérfanas.
- [ ] P12-06 — Validar origin/CSRF/CORS/token de sesión en WS y REST si se abre el frontend fuera de loopback.
- [ ] P12-07 — Ejecutar auditoría de dependencias y lockfiles, gestionar vulnerabilidades relevantes documentadas.
- [ ] P12-08 — Verificar esquema SQLite y migraciones, backups y recuperación ante errores de disco.
- [ ] P12-09 — Probar errores HTTP (`400/404/409/413/422/429/503`) y ausencia de stacktraces sensibles.
- [ ] P12-10 — Medir rendimiento de análisis con archivos de 100 y 1.000 líneas en equipo de referencia; registrar percentiles.
- [ ] P12-11 — Medir impacto de concurrencia y verificar políticas de cuotas configurables.
- [ ] P12-12 — Ejecutar auditoría accesibilidad automática y manual WCAG 2.2 AA en flujos principales.
- [ ] P12-13 — Probar navegador soportado, pantalla pequeña, teclado, tab focus y lectura de errores.
- [ ] P12-14 — Ejecutar lint, tipado, tests unitarios/integración, e2e y coverage; resolver fallos, no silenciarlos.
- [ ] P12-15 — Asegurar política de privacidad local, no telemetría activada por defecto y redacción de secretos en logs.
- [ ] P12-16 — Ejecutar smoke tras reconstrucción de imágenes runtime e instalación limpia.
- [ ] P12-17 — Añadir pipeline CI con reporte de seguridad, cobertura, test diferencial y artifacts de aceptación.

**Salida de hito:** producto con controles y mediciones de calidad verificadas, sin vías conocidas para ejecutar código en host.

## P13 — Revisión integral, documentación final y entrega

- [ ] P13-01 — Auditar RF-01..RF-29 uno a uno; comprobar test, ruta de UI, código real y resultado.
- [ ] P13-02 — Auditar RNF-01..RNF-12 con pruebas, evidencia y estado específico.
- [ ] P13-03 — Revisar todos los botones, menús, campos, pestañas y descargas; demostrar que ninguno es inerte.
- [ ] P13-04 — Desde instalación limpia abrir app, crear archivo inédito, analizarlo, traducirlo, ejecutarlo en ambos destinos y descargarlo.
- [ ] P13-05 — Desde instalación limpia ejecutar A–E 3 casos cada uno en ambos destinos y exportar matriz 30/30.
- [ ] P13-06 — Ejecutar un caso inválido de cada fase y un error runtime, comprobar mensajes y bloqueos.
- [ ] P13-07 — Demostrar WebSocket interactivo: prompt real, respuesta de usuario, salida emitida y fin de proceso.
- [ ] P13-08 — Demostrar un `Mientras` infinito finalizado por timeout y una ejecución detenida manualmente.
- [ ] P13-09 — Demostrar persistencia: crear/guardar/reabrir/duplicar/eliminar, con aviso de cambios pendientes.
- [ ] P13-10 — Generar capturas reales de UI y bitácora/reporte de pruebas con versiones y hashes; no crear mockups como evidencia.
- [ ] P13-11 — Completar `README.md`, manual de usuario, guía técnica, API OpenAPI, ayuda y guía de defensa.
- [ ] P13-12 — Actualizar `docs/IMPLEMENTATION_STATUS.md`, `docs/TRACEABILITY.md` y tabla RF/RNF con estado y evidencia.
- [ ] P13-13 — Enumerar limitaciones **reales** restantes, si alguna, y no declarar producto terminado si contradicen requisito obligatorio.
- [ ] P13-14 — Fijar tag/commit de release, checklist de instalación reproducible y entrega de evidencias verificables.

**Salida de hito:** proyecto íntegramente funcional, instalable, probado, documentado y preparado para defensa.

---

## Tabla de checkpoints / puertas de calidad

| Puerta | Condición necesaria para continuar marcando integración |
|---|---|
| G1: base | Bootstrap reproducible, infraestructura levantada y documentación inicial. |
| G2: compilador | Lexer + parser + semántica y errores robustos sobre A–E y negativos. |
| G3: codegen | PY/JS sintácticamente válidos, semántica equivalente y artefactos descargables. |
| G4: runner | Ejecución real de PY/Node, stdin/stdout/stderr, aislamiento y healthcheck. |
| G5: UI | Editor y controles conectados a API real, resultados no prefijados. |
| G6: suite | 30/30 casos oficiales + inéditos + errores + pruebas de seguridad pasando. |
| G7: release | RF/RNF trazados, instalación limpia, manuales, CI y evidencia sin deuda bloqueante. |

## Plantilla de evidencia por checkbox (completar al cerrar)

```markdown
### P?-XX / RF-??
- Estado: [x] Verificado
- Implementación: `backend/compiler/parser.py:L55-L120` (o rutas reales)
- Prueba: `pytest backend/tests/test_parser.py -q`
- Resultado: `PASSED ...` (salida exacta o enlace a reporte existente)
- Integración: `POST /api/v1/analyze` → inspector AST (si aplica)
- Evidencia: `reports/...` / captura real / logs reales
- Commit: `<hash obtenido de git>`
- Fecha: `<timestamp real>`
- Observaciones: <pendientes conocidos; ninguno si corresponde>
```

## Protocolo cuando aparezcan obstáculos

- **Dependencia faltante:** indicar versión/instalación requerida, comprobar si puede instalarse legal y técnicamente en el entorno; seguir con tareas independientes y no reportar el componente como terminado.
- **Fallo en tests:** reproducir, identificar causa raíz, corregir implementación y repetir tests. No modificar el expected oficial para que coincida con el error.
- **Ambigüedad de fuente académica:** elegir semántica documentada que respete A–E y registrar decisión; no inventar programa F ni alterar salida académica.
- **Sin motor rootless o sin permisos:** dejar explícitamente `RUN_SANDBOX_UNAVAILABLE`; ofrecer pasos concretos de configuración y mantener deshabilitado ejecutar. No ejecutar sin aislamiento ni simular la salida.
- **Falta de credenciales/acciones externas:** no inventar ni imprimir secretos. Solicitar solo la intervención estrictamente necesaria y seguir el resto.
- **Pausa de implementación:** dejar checkpoints, estado y comando «siguiente tarea», sin marcar pendiente como terminado. Reanudar desde `docs/IMPLEMENTATION_STATUS.md` y el plan.

## Criterio de aprobación final, sin excepciones cosméticas

- [ ] Aprobación-01 — Todos RF-01..29 implementados, interconectados y verificables.
- [ ] Aprobación-02 — Todos RNF-01..12 evaluados y satisfechos con evidencia o mediciones.
- [ ] Aprobación-03 — 30/30 ejecuciones académicas reales pasan con Python/Node y salida equivalente.
- [ ] Aprobación-04 — Pruebas inéditas, negativos, errores runtime y seguridad pasan.
- [ ] Aprobación-05 — No existe respuesta de ejecución prefijada, análisis ficticio, botón inerte ni regla particular por ejemplo.
- [ ] Aprobación-06 — Consola batch/interactiva funcional, procesos cancelables y sandbox aislado y disponible.
- [ ] Aprobación-07 — Instalación reproducible y documentación suficiente para un tercero.
- [ ] Aprobación-08 — Informe de trazabilidad completo, con enlaces a código, tests, artefactos y commits reales.

**Regla final:** cuando se cierre la última casilla, ejecutar de nuevo la suite completa. Si falla, reabrir casillas afectadas. El estado «completo» requiere evidencia real actual, no intención de implementación.
