# Pseudo / Studio — Lo exigido frente a lo existente

**Corte inicial:** 24 de octubre de 2026.\
**Contrato académico:** [REQUERIMIENTOS_FASES_2_3.md](REQUERIMIENTOS_FASES_2_3.md).\
**Ejecución del cierre:** [PLAN_CIERRE_FASES_2_3.md](PLAN_CIERRE_FASES_2_3.md).

## 1. Método y límites de la revisión

Se leyó visualmente el PDF completo y se inspeccionaron el compilador, generadores, API de exportación, frontend, pruebas y reportes en disco. La matriz de las secciones 2–6 conserva ese **corte inicial de inspección**; al pie se agrega la revalidación ejecutada después. Para el estado actual, las filas cerradas por esa evidencia posterior reemplazan las brechas de inspección.

HEAD observado: `14b2419b3394d985b93d35514c3b800028060d9c`. El checkout contiene cambios modificados y archivos sin seguimiento, incluidos trabajos previos de compilador, UI, pruebas extendidas y documentación. HEAD por sí solo no identifica todo lo que está en disco. Una entrega deberá capturar también el estado del árbol y los hashes; no atribuir todos los cambios a un commit anterior.

Estados usados:

- **Implementado / evidencia previa:** existe código y evidencia histórica; pendiente repetir para la entrega vigente.
- **Parcial:** existe una base, pero falta comportamiento, explicación o evidencia para el criterio completo.
- **Falta:** no se encontró la capacidad o el entregable en las rutas inspeccionadas.
- **Riesgo por verificar:** la inspección muestra una posible inconsistencia; todavía no equivale a un fallo demostrado mediante ejecución.
- **Bloqueo ambiental previo:** el último intento dependía de un entorno no disponible; hay que comprobar su estado de nuevo.

## 2. Evidencia que ya tenemos

| Evidencia | Resultado registrado | Alcance real |
|---|---|---|
| `reports/acceptance-results.json` | 30/30; `2026-10-17T03:50:01Z` (16 de octubre en El Salvador). | A–E, 15 datasets, Python/Node en OCI; no certifica automáticamente cambios posteriores. |
| `reports/extended-acceptance-results.json` | 45/45; `2026-10-17T03:47:13Z`. | 5 compilaciones, 24 ejecuciones válidas, 6 negativos de compilación y 10 errores runtime. No son 45 programas distintos. |
| `reports/phase1-manual-acceptance.json` | 12/12; `2026-10-24T05:47:49Z` (23 de octubre en El Salvador). | Traducciones **manuales** A/B en Python/Node locales con stdin agrupado; no prueba el generador completo ni el aislamiento. |
| `docs/VALIDATION_REPORT.md`, cierre del 23 de octubre | 43 pruebas + 33 subtests aprobados en el subconjunto sin OCI; 2 métodos OCI deseleccionados en ese subconjunto. | Compilador, fixtures, proyectos y traducciones manuales. La selección no sustituye a la suite completa. |
| Mismo informe, intento de suite completa | 51 passed, 15 failed, 16 errors y 33 subtests. | Runner/API afectados por Docker no disponible; el resultado global no fue aprobado. |
| `docs/Informe_Investigacion_Pseudo_Studio.docx` | Informe Fase 1 corregido, referencias dinámicas de página y figuras de stdout. | Paginación final sin renderizar/verificar en Word/LibreOffice; las figuras añadidas son transcripciones visuales, no capturas de escritorio. |

La última indisponibilidad OCI está documentada el 23 de octubre. **No se afirma que siga caído el 24 sin una nueva comprobación.** El plan comienza verificándolo.

## 3. Matriz de cobertura y brechas

Las tareas C00–C10 se definen en el plan. Todas las rutas son evidencia de inspección, no una afirmación de que fueron ejecutadas hoy.

| Requisito | Lo que tenemos | Estado al corte | Qué falta para cerrar | Trabajo |
|---|---|---|---|---|
| F1-GRAM | `docs/gramatica.ebnf`, lexer/parser y tests; reglas de entero/decimal, cadenas, identificadores, comentarios y `.5`. | Parcial | Consolidar ejemplos por producción y reconciliar la descripción IEEE-754 con las representaciones efectivas; revisar coincidencia del resaltado con el léxico. | C02 |
| F1-DEST | `docs/MANUAL.md`, ADR-010, tabla del DOCX y pestaña Equivalencias en `frontend/src/main.tsx`. | Parcial | Sincronizar tipos y límites entre documentos/UI; justificar precisión, I/O y auxiliares con ejemplos reales. | C02, C04 |
| F1-AB | Cuatro archivos comentados en `examples/phase1-translations/`; batch 12/12 registrado. | Parcial para Estratégico | Incorporar casos adicionales de las traducciones manuales, evidencia interactiva vigente y explicación de optimizaciones que preserven semántica. | C07 |
| F1-DOC | Portada corregida, campos PAGEREF/PAGE y evidencia visual en DOCX. | Parcial | Abrir/renderizar, recalcular y comprobar páginas; revisar roster real y legibilidad; producir PDF final si se entrega PDF. | C07 |
| F2-LEX | `backend/compiler/lexer.py`, `test_lexer.py`, tokens con spans y normalización Unicode. | Implementado / evidencia previa | Matriz token/regla/caso, ejemplos especiales y métricas reproducibles para sustentar eficiencia. | C02, C07 |
| F2-AST | `parser.py`, `model.py`, `_synchronize`, `test_parser.py`, árbol desplegable `AstNode` en la UI. | Parcial | Documentar construcción/recorrido; demostrar recuperación de múltiples errores anidados; mostrar operadores, valores, nombres y relaciones del árbol. | C03, C04 |
| F2-SEM | `semantic.py`: tipos, inicialización, funciones, scopes global/función, símbolos y referencias; `test_semantic.py`. | Implementado / cierre parcial | Documentar reglas y casos; revisar parámetros/retornos, uso antes de inicializar y diagnósticos en combinaciones nuevas; resolver riesgos semánticos confirmados. | C02, C05, C07 |
| F2-ERR | `Diagnostic` tiene código, fase, severidad, mensaje, span y `hint`; UI muestra hints y enfoca fuente. | Parcial | `hint` es opcional y numerosos errores no lo completan; el parser usa una recomendación genérica. Añadir correcciones específicas y demostrar calidad de recuperación. | C03 |
| F2-CD | Fuentes C/D y sus seis datasets; están cubiertos por aceptación oficial previa. | Implementado / evidencia previa | Informe Fase 2 con C/D, consola real, nuevas evidencias de 12 ejecuciones y casos más amplios; no usar solo números globales del reporte. | C01, C07 |
| F2-DOC | Manual técnico, gramática, matrices y un informe académico de Fase 1. | Falta entregable específico | Informe de análisis Fase 2, figuras de AST/símbolos/errores, explicación de algoritmos y guion de defensa correspondiente. | C04, C07 |
| F3-GEN | `backend/generators/codegen.py`: emitters Python/JS, expresiones y sentencias sobre nodos, código completo/resumido y source maps. | Implementado / cierre parcial | Diagrama del recorrido por destino, revisión de casos complejos, comportamiento numérico y evidencia de código idiomático. | C02, C05, C09 |
| F3-DEST | Dos generadores, dos imágenes/runtime y dos paneles de código. | Implementado / evidencia previa | Revalidar ambos, errores y descargas desde el frontend en el estado final. No hace falta un tercer lenguaje. | C01, C08 |
| F3-ARR | `Dimension`, índices 1-based, helpers de límites, funciones y recursión; tests unitarios/OCI existentes. | Parcial / riesgo por verificar | Paso por valor documentado y probado, especialmente si se pasa un array; casos límite de tipos, aliasing, retornos y scopes. | C02, C05 |
| F3-IN | Control de archivo de la UI acepta `.psc,.txt`, lee `file.text()` y limita tamaño. | Implementado / evidencia específica pendiente | Probar A–E importados como `.txt`, UTF-8/CRLF/BOM y archivo inválido; comprobar que la fuente cargada alimenta la compilación vigente. | C06, C08 |
| F3-ERRTXT | Exportación de diagnósticos JSON en API/UI. `ExportKind` no contiene una variante textual. | Falta | Exportador `.txt`, registro/MIME, botón y pruebas de contenido de errores aun con fuente inválida. | C06 |
| F3-CODETXT | Exportaciones `.py` y `.js` completas; no existen tipos TXT en `ExportRegistry.EXTENSIONS`. | Falta | Un `.txt` real por destino con el código autónomo vigente, manteniendo descargas nativas y comprobando igualdad de contenido. | C06 |
| F3-AE | A–E, 15 datasets, consola, comparador y reporte histórico 30/30; E2E recorre el panel oficial. | Implementado / evidencia previa | Nueva corrida final 30/30, entrada `.txt` y ejecución del contenido exportado; evidencia de los dos runtimes y trazabilidad por archivo/caso. | C01, C08 |
| F3-DOC | Documentación general y tabla de equivalencias; no se encontró informe académico específico Fase 3. | Falta entregable específico | Informe de síntesis, resumen Fase 2, diagramas por destino, paquete de archivos, evidencias y defensa. | C09 |
| X-REAL | Reportes JSON/MD con hashes, fechas y runtimes; documentos históricos. | Parcial | Reconciliar fechas y estado del checkout; crear paquete final con procedencia y evidencias vigentes, preservando el historial. | C00, C07, C08, C09 |
| X-HASH | `compile_source`, hashes, UI con estados obsoletos y bloqueo de artefactos inválidos. | Implementado / evidencia previa | Extender la misma garantía a los nuevos `.txt` y probar edición → exportación. | C06, C08 |
| X-SAFE | `backend/runtime/runner.py`, controles OCI y pruebas de aislamiento; espera interactiva corregida previamente. | Bloqueo ambiental previo | Verificar el engine; demostrar controles y volver a correr integración. Nunca sustituir el runner de la app por ejecución directa en host. | C01, C08 |
| X-COMP | `examples/extended/`, casos válidos/negativos/runtime, Hypothesis y pruebas de conformidad. | Implementado / ampliar evidencia | Matriz de combinaciones y regresiones derivadas de los riesgos; pruebas inéditas no equivalen a garantizar cualquier programa posible. | C03, C05, C08 |

## 4. Hallazgos concretos que cambian el plan

### 4.1 Formatos TXT: una falta confirmada

Revisados `backend/app/schemas.py::ExportKind`, `backend/app/main.py::ExportRegistry` y `create_export`. Las salidas disponibles incluyen `.psc`, `.py`, `.js`, JSON, Markdown y PDF, pero no código/errores `.txt`. La entrada `.txt` **sí existe** en la UI. Se amplía el flujo actual de exportación; no se necesita construir un segundo compilador ni un sistema de archivos nuevo.

### 4.2 AST: el árbol ya existe; la información explicativa es parcial

`frontend/src/main.tsx::AstNode` renderiza `kind`, `node_id`, ubicación y nodos hijos. Omite en su presentación atributos escalares como operador, valor literal e identificador, y no imprime las etiquetas de cada relación padre/hijo. Esto dificulta explicar por qué `a + b * c` difiere de `(a + b) * c`, aunque el parser sí tenga esa estructura. Es una mejora concreta de lectura del árbol existente.

### 4.3 Errores: formato listo, sugerencias insuficientes

`backend/compiler/model.py::Diagnostic` permite `hint=None`; `SemanticAnalyzer._diag` también. `Parser._fail` usa «Revise la gramática y el terminador correspondiente». Hay recuperación por newline/terminadores en `_synchronize`, por lo que no se describe como ausente. Falta convertir esa base en sugerencias contextuales y demostrar recuperación útil para obtener la evidencia que pide el nivel Estratégico.

### 4.4 Número y parámetros: riesgos a demostrar antes de cerrarlos

| Riesgo observado | Evidencia estática | Experimento de aceptación pendiente |
|---|---|---|
| Diferencia de precisión entre destinos | `BaseEmitter.expression` convierte el literal a float y emite sintaxis de entero si es integral; Python luego puede operar con enteros de precisión arbitraria, mientras JS usa Number. | Expresiones cercanas a `2^53`, productos grandes y mezclas con fracciones; fijar contrato común y comparar salidas/resultados. No se afirma aquí un resultado ejecutado. |
| Array como argumento puede compartir objeto | `Call` emite argumentos directamente; no se observa una copia de array en ese punto. | Función que modifica un elemento y posterior lectura del array original, en ambos destinos. Si el contrato es paso por valor para arrays, el original debe permanecer igual. |
| Spans Unicode frente a selección del editor | Backend cuenta caracteres; `Editor.focusSpan` usa posiciones del documento CodeMirror. | Introducir un carácter fuera del BMP antes de un error y comprobar selección exacta; convertir unidades si se demuestra desfase. |
| Errores sintácticos encadenados | Recuperación existente por salto de línea/cierre; el servicio puede analizar un árbol recuperado y bloquea generación por diagnósticos. | Dos errores independientes en bloques anidados: ambos detectados, sin bucle ni cascada engañosa, artefactos vacíos. |

Estos riesgos deben originar pruebas dirigidas, no correcciones basadas únicamente en suposición. Si una capacidad no está admitida por la gramática, debe rechazarse con diagnóstico claro y documentarse; si sí está admitida, debe funcionar conforme a su contrato.

## 5. Prioridades y qué reutilizar

1. **Fase 2 primero:** reglas coherentes, sugerencias y recuperación, explicación del AST, informe propio y evidencia C/D. Gestor de errores pesa 25% en esa fase.
2. **Cerrar la falta explícita de Fase 3:** código y errores `.txt` en API/UI y pruebas de importación/exportación. Funcionamiento integral pesa 25% en esa fase.
3. **Robustez:** resolver riesgos demostrados de números, funciones/arrays y errores; ampliar evidencia usando las suites existentes.
4. **Entrega:** revalidación aislada, documentos por fase, PDF revisado y guion de defensa. No confundir figuras reconstruidas a partir de stdout con capturas de la interfaz.

Se reutilizan `compile_source`, el AST tipado, `SemanticAnalyzer`, los dos emitters, el registro de exportaciones, `OciRunner`, los fixtures y el comparador. No se propone migración de stack ni reescritura de módulos que ya resuelven el problema.

## 6. Pendientes del contrato original, fuera de los pesos nuevos

`docs/REMAINING_GATES.md` conserva accesibilidad manual y cobertura multiplataforma pendientes. La CI remota fue dispensada y continúa sin evidencia de ejecución. No se suman esos asuntos como criterios inventados del nuevo PDF ni se borran del compromiso global. El estado histórico de servicios descrito en documentos antiguos debe leerse con su fecha; no demuestra servicios activos hoy.

No se calcula una nota estimada ni un porcentaje global a partir de esta inspección: mezcla implementación, presentación académica y pruebas que requieren nueva ejecución. Cada fila se cerrará con la evidencia indicada en el plan.

## 7. Revalidación y brechas cerradas — 2026-10-24

La revalidación cubrió el árbol de trabajo con Docker Desktop VM disponible. Evidencia completa y comandos en [VALIDATION_REPORT.md](VALIDATION_REPORT.md); el estado por requisito está en [TRACEABILITY.md](TRACEABILITY.md).

| Brecha identificada en el corte inicial | Estado luego de implementar y ejecutar | Evidencia vigente |
|---|---|---|
| Contrato léxico/semántico disperso y resaltado `Modulo` | Cerrada en el código/documentos actuales; matriz de producción → nodo → caso y regla de tipos/ámbitos/numéricos disponible. | `docs/LANGUAGE_CONFORMANCE_MATRIX.md`; pruebas de conformidad; test E2E de resaltado. |
| Diferencia de enteros grandes Python/JavaScript y arrays compartidos por argumento | Corregida con representación común de doble precisión y copia 1D de parámetro; se ejecutó en ambos runtimes. | `backend/tests/test_runner_integration.py`; `reports/extended-acceptance-results.json`. |
| Sugerencias genéricas, recuperación y foco Unicode | Hints específicos por diagnóstico; error múltiple anidado recupera sin traducir; conversión de spans a UTF-16 comprobada en UI. | `docs/NEGATIVE_TEST_MATRIX.md`; parser/semántica; E2E error→reparación/reanálisis. |
| AST difícil de explicar | Vista muestra metadata escalar y relaciones con etiqueta; informe describe Pratt, spans y emisión. | `docs/AST_Y_RECORRIDO.md`; pruebas Playwright; captura de C/D. |
| Exportaciones TXT de código y errores ausentes | Implementadas en API/UI; texto de código igual al artefacto completo; archivo inválido permite diagnóstico y bloquea código. | `backend/tests/test_exports_txt.py`, `backend/tests/test_api.py`, `frontend/e2e/compiler-exports.spec.ts`. |
| Runtime/acceptance antiguo no correspondía al árbol actual | Verificado de nuevo en OCI: A–E 30/30 y casos extendidos 54/54; suite backend y E2E 10/10. | `reports/acceptance-results.json`, `reports/extended-acceptance-results.json`, `frontend/playwright-report/`, `docs/VALIDATION_REPORT.md`. |
| Evidencia de ejecución/entrega sin paquete actualizado | Paquete Phase 3 contiene fuentes, código generado, errores, casos ampliados, reportes y capturas con manifiesto de hashes. | `delivery/fase-3/README.md`, `delivery/fase-3/SHA256SUMS`. |

### Pendientes que no se dan por cerrados

- El render final del DOCX/PDF y la paginación no se pudieron revisar en Word/LibreOffice; hace falta completar nombres reales del equipo.
- No se ejecutó la auditoría manual con lector de pantalla ni una instalación nativa macOS/Linux rootless.
- La verificación CI remota está dispensada por el usuario y no se registra como aprobada.
- Entrega/defensa institucional dependen de acciones humanas. Los resultados locales no son una nota asignada por el docente.
