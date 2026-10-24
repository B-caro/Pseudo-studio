# Pseudo / Studio — Plan de construcción y entrega de Fases 2 y 3

**Versión:** 1, 24 de octubre de 2026.\
**Requisitos:** [REQUERIMIENTOS_FASES_2_3.md](REQUERIMIENTOS_FASES_2_3.md).\
**Base y brechas:** [MATRIZ_BRECHAS_RUBRICAS.md](MATRIZ_BRECHAS_RUBRICAS.md).\
**Meta:** cerrar las exigencias de ambas fases y reunir evidencia para el nivel Estratégico, aprovechando la implementación existente.

## 1. Reglas para ejecutar el plan

1. Las casillas representan trabajo de cierre; la matriz documenta qué código ya existe. No reconstruir el lexer, parser, generadores o runner solo porque una casilla de aceptación esté pendiente.
2. Para cada tarea: inspeccionar → implementar si falta → comprobar con casos pertinentes → corregir → guardar evidencia → actualizar estado. Marcar `[x]` únicamente después de verificar su criterio de salida.
3. Registrar fecha, entorno, comandos y exit codes, resultados, archivos y hashes. Al integrar cambios, registrar el commit real. Si la comprobación se hace con cambios sin commit, identificar el diff/árbol; no atribuirlos al HEAD anterior.
4. Mantener algoritmos, prompts y resultados oficiales A–E. Los casos ampliados tienen su propio nombre y expectativa razonada. No cambiar el oráculo para hacer pasar una prueba.
5. Mantener las pruebas existentes. Una suite seleccionada ayuda a trabajar con Docker ausente, pero no cierra la aceptación integral.
6. La indisponibilidad del runner bloquea las pruebas OCI, no la escritura del informe, el análisis estático o el trabajo del compilador. No ejecutar código de usuario sin aislamiento como sustituto de aceptación de la app.
7. Estado de ejecución 2026-10-24: **57/63 tareas verificadas**. C01–C06 y el trabajo técnico ejecutable de C07–C08 se verifican con comandos reales en [VALIDATION_REPORT.md](VALIDATION_REPORT.md); suite backend, E2E y OCI pasan. La suite ampliada actual es 54/54 e incluye ordenamiento/búsqueda, dimensiones cero/negativas/fraccionarias y overflow. C09 tiene informes y paquete reproducible, pero render académico y ensayo humano siguen abiertos; C10 conserva los gates manuales y multiplataforma. Las casillas de abajo distinguen esos límites.

## 2. Dependencias y prioridades

| Paquete | Resultado esperado | Dependencias | Prioridad |
|---|---|---|---|
| C00 | Requisitos, inventario y contraste documentados. | PDF y checkout. | Completado en planificación |
| C01 | Entorno OCI comprobado y evidencia reproducible. | C00. | Alta; bloquea la demostración real |
| C02 | Gramática, tipos y semántica de parámetros coherentes. | C00. | Alta para ambas fases |
| C03 | Errores accionables y recuperación demostrada. | C02. | Alta, 25% de Fase 2 |
| C04 | AST comprensible y material de recorrido. | C02; C03 para mostrar errores. | Alta para Fase 2 |
| C05 | Casos complejos, números, funciones y arrays comprobados. | C02; C01 para runtime. | Alta para defectos confirmados; resto antes de Fase 3 |
| C06 | Entrada/salida `.txt` integrada en API y UI. | C00 y contrato TXT; C03 para sugerencias. | Alta, falta funcional explícita |
| C07 | Informe, evidencia y defensa de Fase 2; cierre editorial Fase 1. | C01–C04 y defectos bloqueantes encontrados en C05. | Gate del 8 de noviembre |
| C08 | A–E y casos complejos desde archivos, UI y runtime. | C01, C03, C05, C06. | Gate técnico de Fase 3 |
| C09 | Informe final, diagramas, archivos y defensa Fase 3. | C04, C07, C08. | Gate del 29 de noviembre |
| C10 | Pendientes originales de accesibilidad/plataformas. | App estable, entorno correspondiente. | Cierre global; no peso nuevo inventado |

Ruta crítica Fase 2: C00 → C02 → C03/C04 → C07, con C01 disponible y cualquier defecto semántico bloqueante resuelto. Ruta crítica Fase 3: C02 → C05 y C06 → C08 → C09. C06 puede adelantarse sin esperar a entregar Fase 2.

## 3. Trabajo por paquete

### C00 — Base documentada

- [x] Revisar las 11 páginas del PDF, incluidas las tres rúbricas y los 15 casos A–E.
- [x] Contrastar las exigencias con las rutas de implementación, pruebas, reportes y entregables existentes.
- [x] Redactar requisitos, matriz de brechas y este plan, distinguiendo implementación, evidencia histórica y verificaciones pendientes.

**Salida:** los tres Markdown de esta entrega. No equivale a cierre funcional de las fases.

### C01 — Recuperar una base ejecutable y trazable

**Requisitos:** X-REAL, X-SAFE, F2-CD, F3-DEST, F3-AE.\
**Reutilizar:** `scripts/manage.py`, `sandbox/`, `backend/runtime/runner.py`.

- [x] Registrar versiones de Python/Node, estado Git y hashes de fuentes; identificar cambios previos para conservarlos al integrar.
- [x] Ejecutar `python3.12 scripts/manage.py verify` y guardar el resultado completo. El último bloqueo fue Docker/OCI no disponible; no asumir que persiste o que ya está resuelto.
- [x] Si falla, documentar causa y acción exacta. Para el entorno WSL previo, comprobar Docker Desktop y su integración con esta distro. No solicitar credenciales ni instalar paquetes privilegiados si no son necesarios/autorizados.
- [x] Con controles disponibles, iniciar con `python3.12 scripts/manage.py start` y ejecutar `python3.12 scripts/manage.py smoke`; registrar ambos runtimes, aislamiento y salud de la app.
- [x] Preparar carpetas de evidencia fechadas y preservar los reportes históricos antes de correr scripts que los sobrescriben. Al finalizar una sesión, declarar si los servicios quedan activos o se detienen.

**Aceptación:** controles del aislamiento verificados y smoke real en Python/Node; si existe bloqueo, permanece abierto y se avanza con C02/C03/C04/C06. **Evidencia propuesta:** `reports/entregas/entorno/` con versiones, verify, smoke y manifiesto de hashes.

### C02 — Consolidar el contrato del lenguaje

**Requisitos:** F1-GRAM, F1-DEST, F2-LEX, F2-SEM, F3-ARR, X-COMP.\
**Reutilizar:** gramática, manual, ADRs, lexer/parser, semántica y equivalencias de la UI.

- [x] Crear la matriz regla → token/nodo → ejemplo válido → inválido → diagnóstico esperado. Cubrir `Leer`, `LeerTexto`, `Escribir`, asignaciones, condiciones, ciclos, arrays, funciones, retornos y expresiones.
- [x] Comprobar/documentar entero y decimal bajo `number`, cadenas, booleanos, nombres Unicode/NFC, comentarios, escapes, operadores compuestos y `.5`.
- [x] Decidir y registrar el modelo numérico común antes de corregir el emisor: precisión, redondeo, overflow, división, módulo y salida textual. Preferencia de partida: hacer cumplir el modelo común ya anunciado en EBNF, validándolo en ambos destinos.
- [x] Precisar ámbitos existentes (global/función), declaración implícita, inferencia, inicialización y retornos. Documentar lo que el lenguaje acepta; no presentarlo como sintaxis PSeInt completa.
- [x] Definir paso por valor para escalares y política de arrays como parámetros. Si se aceptan arrays por valor, establecer copia 1D y pruebas de independencia; no confundir reasignación de parámetro con mutación de un elemento compartido.
- [x] Sincronizar EBNF, manual, informe y tabla de equivalencias. Revisar resaltado de `Modulo` y caracteres Unicode como consistencia de presentación, sin convertirlo en validador semántico.

**Aceptación:** contrato sin contradicciones conocidas y ejemplos verificables para cada familia; decisiones numéricas/arrays enlazadas a C05. **Entregables propuestos:** `docs/LANGUAGE_CONFORMANCE_MATRIX.md` y ADRs necesarios. Las decisiones deben estar resueltas antes de presentar como completo el sistema de tipos.

### C03 — Completar errores y recuperación

**Requisitos:** F2-AST, F2-ERR, X-COMP.\
**Reutilizar:** `Diagnostic`, `_synchronize`, `_fail`, `_diag`, inspector y matriz negativa.

- [x] Inventariar los códigos léxicos/sintácticos/semánticos y su hint actual. Construir un catálogo con causa, ubicación y corrección específica.
- [x] Completar sugerencias: variable desconocida, uso no inicializado, mezcla de tipos, aridad, cierre faltante, paréntesis, cadena sin cerrar, dimensión/índice inválidos y división constante entre cero. Evitar que todos recomienden genéricamente revisar la gramática.
- [x] Probar al menos dos errores independientes dentro de bloques anidados; recuperar al siguiente punto válido y evitar cascadas redundantes o bucles.
- [x] Mantener `translatable=false` y artefactos vacíos cuando haya errores. Si se muestra un AST parcial, identificarlo como recuperado/inválido; no tratarlo como prueba de compilación exitosa.
- [x] Comprobar que el span selecciona la fuente correcta, incluyendo Unicode fuera del BMP; corregir unidades de offset si el experimento demuestra desfase.
- [x] Comprobar coherencia de diagnóstico entre API, inspector, foco de editor y exportaciones. Actualizar `docs/NEGATIVE_TEST_MATRIX.md` con resultado y evidencia.

**Aceptación:** casos cubiertos con diagnóstico completo, sugerencia útil y ubicación correcta; recuperación finita comprobada; ninguna traducción inválida habilitada. **Pruebas:** ampliar lexer/parser/semántica/conformidad y E2E solo donde haya un nuevo comportamiento.

### C04 — Hacer defendible el AST y su recorrido

**Requisitos:** F2-AST, F2-DOC, F3-GEN, F3-DOC.\
**Reutilizar:** `model.py`, `parser.py`, `AstNode`, `MappedCode`, mapas de fuente y modo Defensa.

- [x] Mostrar operador, valor, identificador y tipo inferido cuando apliquen, además de `kind`, ID y span. Mostrar nombres de relaciones como condición, cuerpo, izquierda/derecha y argumentos.
- [x] Conservar navegación árbol → fuente y código generado → fuente; verificar contenido largo, escape de texto y navegación por teclado.
- [x] Preparar un ejemplo de construcción de AST para `((a + b) * c) - (a / b)` y explicar precedencia, agrupación y por qué los paréntesis pueden desaparecer como tokens estructurales en el árbol.
- [x] Documentar el algoritmo real del parser, puntos de recuperación y relación con símbolos/semántica. Incluir un ejemplo C o D con ciclos/índices y uno E con función/llamada.
- [x] Elaborar diagramas de recorrido AST → regla de emisión → Python y AST → regla de emisión → JavaScript, con vínculos a funciones reales del generador y a helpers necesarios.

**Aceptación:** una persona puede identificar operandos y explicar qué nodo produce una línea destino usando la UI y el informe. **Entregables propuestos:** `docs/AST_Y_RECORRIDO.md` y figuras reproducibles. Un recorrido animado paso a paso es opcional después de cubrir esto; no es una dependencia de entrega.

### C05 — Validar y corregir semántica en casos complejos

**Requisitos:** F2-SEM, F3-GEN, F3-ARR, X-COMP.\
**Reutilizar:** pruebas unitarias, `examples/extended/`, Hypothesis y runner OCI.

- [x] Comprobar los riesgos numéricos identificados: entorno de `2^53`, productos grandes, operandos decimales, módulo negativo, división y resultados no finitos. Registrar cada diferencia observada y aplicar la política C02 a ambos destinos.
- [x] Probar reasignación de parámetros escalares, alias de retorno, retorno textual/numérico, aridad, recursión, llamadas adelantadas y nombres iguales en distintos ámbitos.
- [x] Probar paso de arrays a funciones, mutación y retorno cuando estén admitidos. Implementar copia por valor si ese es el contrato fijado en C02; verificar además el tipo de sus elementos.
- [x] Cubrir dimensión 0/negativa/fraccionaria, índices 0/n/n+1, elemento sin inicializar, arrays en bucles anidados y límites inclusivos de `Para` con dirección/paso.
- [x] Agregar combinaciones inéditas: búsqueda/ordenamiento de arreglo, operaciones con funciones y acumuladores, texto/booleanos/cortocircuito, errores múltiples. Escribir expectativas independientes del compilador y revisar cada algoritmo.
- [x] Revisar la salida idiomática de ambos emitters: bloques, expresiones, funciones y auxiliares comprensibles, conservando evaluación, I/O y errores. Documentar mejoras justificadas; no introducir optimizaciones que cambien efectos observables.
- [x] Para cada defecto confirmado, corregir la causa, añadir regresión y repetir pruebas afectadas; regenerar snapshots solo después de justificar el cambio de generación, nunca para ocultar una diferencia.

**Aceptación:** cero divergencias observadas en el contrato probado; errores previstos con código/ubicación y comportamiento equivalente. La suite vigente suma 54 checks (45 anteriores + casos nuevos); esa cifra no se presenta como prueba de exhaustividad de la gramática.

### C06 — Completar los archivos TXT exigidos

**Requisitos:** F3-IN, F3-ERRTXT, F3-CODETXT, X-HASH.\
**Reutilizar:** `ExportRequest`, `ExportKind`, `ExportRegistry`, `create_export`, `exportArtifact` y carga de archivos.

- [x] Ampliar contrato API con `python-txt`, `javascript-txt` y `diagnostics-txt`, MIME textual y nombres distinguibles por destino; actualizar documentación de rutas.
- [x] Generar TXT de Python/JS desde el artefacto completo, incluyendo auxiliares. Conservar los bytes del código nativo correspondiente; evitar exportar solamente la vista resumida.
- [x] Generar errores TXT legibles, con fase/código/ubicación/mensaje/hint y hash. Permitir exportación de errores cuando la compilación sea inválida y bloquear exportación de código en ese caso.
- [x] Añadir controles de descarga claros en Traducción y Errores, integrados al exportador real; conservar `.py`, `.js` y JSON.
- [x] Probar desde el frontend A–E en `.txt`, UTF-8/tildes/CRLF, tratamiento de BOM y fallo de carga; no introducir cambios invisibles que invaliden spans/hashes.
- [x] Probar fuente válida, fuente inválida, edición tras traducir, nombre/MIME/UTF-8 y contenido descargado. La descarga debe corresponder a la fuente vigente.
- [x] Copiar el contenido TXT descargado a `.py`/`.js` sin editarlo y ejecutar esa copia en el runtime aislado; comparar con el artefacto original. Guardar ambos hashes y resultados.

**Aceptación:** prueba completa archivo `.txt` → compilación → dos `.txt` ejecutables y errores `.txt` cuando corresponda, desde UI y API. **Pruebas propuestas:** casos nuevos en `test_api.py` y `frontend/e2e/workbench.spec.ts` o archivo específico de exportaciones.

### C07 — Cerrar Fase 2 y la presentación heredada

**Requisitos:** F1-AB, F1-DOC, F2-LEX, F2-AST, F2-SEM, F2-ERR, F2-CD, F2-DOC, X-REAL.

- [x] Ejecutar C y D con sus tres datasets en Python y Node; guardar 12 registros completos y evidencia visible de consola. Etiquetar cada captura con caso/destino/entrada, sin fingir una captura mediante una imagen ilustrativa.
- [x] Mostrar un programa inédito que combine estructuras y ejemplos negativos por fase. Demostrar recuperación, sugerencia y corrección seguida de nuevo análisis real.
- [x] Actualizar/ejecutar las pruebas adicionales de A/B manuales con lote e interacción, y verificar que el problema de stdin agrupado siga resuelto; conservar 12/12 oficiales separados de pruebas adicionales y explicar mejoras de I/O/legibilidad sin alterar el algoritmo.
- [x] Medir análisis de fuentes de 100 y 1.000 líneas y casos de recuperación, registrando tiempo por fase, tamaño y entorno. Reutilizar `scripts/benchmark_compile.py` y las duraciones de `compile_source`; justificar eficiencia con medidas, sin inventar umbrales del docente.
- [x] Preparar `docs/INFORME_FASE_2.md`: portada, objetivos, reglas léxicas/tipos, diseño de parser/AST, símbolos/scopes, errores/recuperación, prototipo C/D, casos adicionales, resultados, límites y referencias.
- [x] Preparar `docs/GUION_DEFENSA_FASE_2.md` con clics reales: cargar C/D → analizar → tokens → AST → símbolos → error y corrección → consola y casos. Incluir respuestas sobre tipos, scopes, recuperación y AST.
- [ ] Renderizar/revisar la versión entregable: portada, integrantes reales, índice, numeración, tablas y figuras legibles. Para el DOCX previo, actualizar campos en Word/LibreOffice y comprobar el PDF final si se utiliza ese formato.
- [x] Revisar las cinco filas de la rúbrica Fase 2; cada una debe enlazar explicación, implementación y evidencia. Registrar bloqueos pendientes sin convertirlos en aprobaciones.

**Gate Fase 2:** C/D 12/12 en el compromiso de dos runtimes, análisis/errores demostrables, documento propio revisado y defensa ensayada. Guardar evidencias bajo `reports/entregas/fase2/`. La entrega en Aula Digital y la asistencia a defensa son acciones humanas, no realizadas por este plan.

### C08 — Aceptación integral de Fase 3

**Requisitos:** F3-GEN, F3-DEST, F3-ARR, F3-IN, F3-ERRTXT, F3-CODETXT, F3-AE, X-REAL, X-HASH, X-SAFE, X-COMP.

- [x] Con entorno comprobado, ejecutar la suite backend completa y corregir defectos. Si falla OCI, registrar bloqueo y no declarar verde el resultado global.
- [x] Ejecutar 30/30 oficiales con fuentes A–E intactas; ejecutar también los casos extendidos actualizados y los negativos añadidos.
- [x] Repetir el circuito de los cinco `.txt` desde UI: cargar, analizar, traducir, exportar ambos destinos, ejecutar y comparar. Validar errores TXT desde una fuente con errores reales.
- [x] Verificar stdin agrupado e interacción pausada por el usuario en ambos runtimes, cancelación, controles de ejecución y bloqueo de compilación obsoleta.
- [x] Ejecutar E2E, build y controles de calidad correspondientes; comprobar que Equivalencias y las nuevas descargas forman parte de la navegación real, sin botones pendientes.
- [x] Repetir el arranque y smoke de la app, registrar entorno/resultados/hash y detener los servicios al terminar.
- [ ] Reproducir la instalación desde un checkout limpio con el bootstrap vigente; registrar hashes de esa instalación y de los artefactos.

**Gate técnico Fase 3:** flujo TXT completo y comprobado, 30/30 oficiales, 54/54 extendidos y negativos vigentes sin defectos bloqueantes, runtime aislado operativo y UI integrada. Instalación limpia todavía no se repitió en esta revisión; el arranque local sí pasó.

### C09 — Documento final, paquete y defensa

**Requisitos:** F3-DOC y trazabilidad de toda Fase 3.

- [x] Preparar `docs/INFORME_FASE_3.md`: carátula, resumen de Fase 2, recorrido del AST, reglas de emisión por destino, diagramas, tipos/funciones/arrays, TXT, pruebas y conclusiones sustentadas.
- [x] Preparar `docs/GUION_DEFENSA_FASE_3.md`: ingresar archivo real, inspeccionar AST, explicar dos reglas de generación, descargar TXT/código, ejecutar ambos destinos, demostrar error y corregirlo.
- [x] Armar paquete con instrucciones de arranque, fuentes oficiales `.txt`, código generado por destino, ejemplos de reporte de errores, evidencia A–E y casos extra, documentos y manifiesto de hashes. Los artefactos del compilador se regeneran; no se sustituyen por las traducciones manuales A/B.
- [ ] Revisar presentación final y referencias; comprobar todos los enlaces y números de página del formato entregado, sin campos «Actualizar» visibles ni datos de integrantes inventados.
- [ ] Ensayar defensa sobre una fuente nueva compatible con la gramática y confirmar que la explicación se apoya en código que efectivamente existe.
- [x] Auditar las cinco filas de la rúbrica Fase 3 y anotar resultado/evidencia por fila. Registrar el commit o estado exacto de entrega y las limitaciones remanentes.

**Gate documental Fase 3:** paquete reproducible y revisado, informe con diagramas por destino y defensa coherente con la demostración. Un PDF de resultados de tests no sustituye al informe académico de síntesis.

### C10 — Cierre global del producto, separado de la rúbrica

- [ ] Completar auditoría manual WCAG de teclado/lector de pantalla/contraste con evidencia, según `docs/REMAINING_GATES.md`.
- [ ] Validar plataformas adicionales que el contrato promete, con entornos reales y registros; una corrida WSL2 no prueba macOS ni Linux rootless nativo.
- [x] Reconciliar `IMPLEMENTATION_STATUS.md`, `TRACEABILITY.md`, `VALIDATION_REPORT.md` y `REMAINING_GATES.md` con el estado final y la fecha de cada evidencia. Mantener CI remota como dispensada y sin verificar, salvo instrucción posterior del usuario.

## 4. Calendario propuesto

Fechas de trabajo propuestas, usando el supuesto de año 2026. No sustituyen la programación de Aula Digital ni asignan personas sin confirmar el equipo.

| Ventana | Trabajo | Salida |
|---|---|---|
| 24–25 octubre | C00/C01, clasificación de riesgos y preservación del trabajo previo. | Base documental y entorno comprobado o bloqueo preciso. |
| 26–28 octubre | C02; pruebas dirigidas de riesgos que condicionan tipos/semántica. | Contrato consistente y alcance exacto de correcciones. |
| 29 octubre–2 noviembre | C03/C04 y defectos bloqueantes de C05. | Errores útiles, AST explicable y regresiones. |
| 3–6 noviembre | C07, C/D, evidencia y documento. | Candidato de Fase 2. |
| 7 noviembre | Revisión editorial y ensayo. | Gate Fase 2 cerrado. |
| 8 noviembre | Entrega/defensa indicada por el PDF. | Acción en Aula Digital según docente. |
| 9–13 noviembre | C06 y C05 pendiente de arrays/funciones y casos complejos. | Flujo TXT y semántica robusta. |
| 14–20 noviembre | C08, suite final, E2E y reparación de fallos. | Evidencia vigente completa. |
| 21–26 noviembre | C09, diagramas, informe y paquete. | Candidato de Fase 3. |
| 27–28 noviembre | Revisión final y ensayo con fuente nueva. | Gate técnico/documental cerrado. |
| 29 noviembre | Entrega/defensa indicada por el PDF. | Acción en Aula Digital según docente. |

Si Docker bloquea la ejecución, avanzar documentación/compilador/exportación y resolver el entorno antes de las ventanas de evidencia. Si falta tiempo, priorizar obligaciones explícitas y defectos reales; no recortar el oráculo oficial, la seguridad ni los dos destinos. La animación del AST y un tercer lenguaje no están en la ruta crítica.

## 5. Comandos de comprobación existentes

Ejecutar desde la raíz; no son resultados nuevos de este documento. Archivar reportes previos antes de scripts que escriben en `reports/`.

```bash
# Habilitación y smoke: verificar primero y detener esta secuencia si falla.
python3.12 scripts/manage.py verify
python3.12 scripts/manage.py start
python3.12 scripts/manage.py smoke

# Análisis y generación, para trabajo que no requiere OCI.
.venv/bin/pytest -q backend/tests/test_lexer.py backend/tests/test_parser.py backend/tests/test_semantic.py backend/tests/test_compiler_service.py backend/tests/test_codegen.py backend/tests/test_codegen_snapshots.py backend/tests/test_language_conformance.py

# Regresión de traducciones manuales Fase 1: ejecución local, no acredita aislamiento.
python3.12 scripts/run_phase1_manual_acceptance.py

# Aceptación integral, únicamente con OCI comprobado.
.venv/bin/pytest -q
python3.12 scripts/run_official_acceptance.py
python3.12 scripts/run_extended_acceptance.py

# Calidad e interfaz.
.venv/bin/ruff check backend scripts
.venv/bin/ruff format --check backend scripts
npm --prefix frontend run build
npm --prefix frontend run test:e2e
git diff --check
```

Las nuevas pruebas TXT/hints/AST se añaden a las suites pertinentes y quedan incluidas en los comandos globales. `scripts/validate_wsl.sh` y `docs/WSL_TEST_PLAN.md` aportan el procedimiento existente de instalación limpia; revisar sus prerrequisitos antes de ejecutarlo. La validación de contenido no debe limitarse a que un snapshot coincida: comprobar comportamiento y resultados con expectativas independientes.

## 6. Registro de avance y entrega

Por tarea terminada registrar:

```text
Tarea: Cxx / requisito(s): ...
Estado: pendiente | en curso | verificado | bloqueado
Cambio y rutas: ...
Pruebas/comandos, fecha, entorno y exit code: ...
Resultado esperado y real: ...
Evidencia: archivo/log/captura + hashes
Estado de código: commit real + cambios locales relevantes
Limitación o bloqueo remanente: ...
```

Estructura de paquete propuesta (a crear durante ejecución):

```text
entrega-fase-2-o-3/
  LEEME.md
  informe/                 # Informe y versión renderizada revisada.
  fuentes/                 # A.txt ... E.txt, según alcance de fase.
  traducciones/            # .python.txt/.javascript.txt y archivos nativos.
  errores/                 # Fuentes negativas y sus reportes TXT.
  evidencia/               # Casos, inputs, stdout/stderr, capturas y versiones.
  SHA256SUMS
```

Las instrucciones indicarán cómo obtener el código fuente del producto y arrancarlo con sus dependencias. No incluir secretos, bases de datos personales, `.venv` o `node_modules` en el paquete. Cada archivo futuro de este plan es una ruta propuesta; su mención aquí no implica que ya exista.
