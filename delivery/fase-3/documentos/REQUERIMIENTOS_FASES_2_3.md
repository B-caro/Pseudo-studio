# Pseudo / Studio — Requerimientos de cierre según las rúbricas académicas

**Fecha de análisis:** 24 de octubre de 2026.\
**Estado:** especificación de trabajo; no certifica que los pendientes estén implementados.\
**Documentos asociados:** [matriz de brechas](MATRIZ_BRECHAS_RUBRICAS.md) y [plan de cierre](PLAN_CIERRE_FASES_2_3.md).

## 1. Fuente y alcance

Se revisaron visualmente las **11 páginas** de `req.pdf`, porque el archivo contiene páginas rasterizadas sin texto extraíble. Su SHA-256 es `d51491e13b40d17795a43326ea35809cb5efcff3929682b9b770c640cef3a5fe`.

Copia idéntica conservada en el proyecto: [req_fases_1_2_3.pdf](../Context/req_fases_1_2_3.pdf).

Original recibido: `/home/bucaro/.t3/userdata/attachments/cf6a37b1-c77c-443c-8d72-36a8f018f4c5-a15b7317-192c-4866-ad0a-c25d063f877c-pdf.pdf`.

Las referencias siguientes utilizan el número físico de página del PDF, comenzando en 1:

| Páginas | Contenido y autoridad |
|---|---|
| 1 | Actividad Fase 2: análisis léxico, sintáctico/AST, semántico, símbolos, errores, documento y defensa. |
| 2 | Actividad Fase 3: síntesis desde AST, dos destinos como mínimo, diagramas, entrada `.txt`, errores `.txt` y código traducido `.txt`. |
| 3, 7 | Presentación y rúbrica de Fase 1. |
| 4–6 | Algoritmos A–E y sus 15 casos oficiales; salida obligatoria en consola. |
| 8, 9 | Presentación y rúbrica de Fase 2. |
| 10, 11 | Presentación y rúbrica de Fase 3. |

Este documento convierte el nuevo PDF en criterios de construcción y aceptación. Se conserva el contrato operativo anterior para seguridad, persistencia, hashes, interfaz y runtimes; el nuevo PDF añade los formatos y entregables académicos que no estaban cubiertos. Ante una contradicción, registrar ambos textos y la decisión: no modificar un caso oficial ni reducir una obligación silenciosamente.

La revisión de Fase 1 recibida anteriormente también se conserva como entrada: tipos y reglas léxicas explícitos, equivalencias justificadas, stdin en lote para JavaScript, comentarios y presentación editorial. El nuevo PDF no contiene esa calificación individual de 8.50; procede del feedback previo.

## 2. Entregas y calendario

| Fase | Peso indicado | Entrega/defensa indicada | Alcance |
|---|---:|---|---|
| 1 | 20% | 11 de octubre, semana 11 | Gramática, destinos y traducciones manuales A/B. |
| 2 | 20% | 8 de noviembre, semana 15 | Análisis, AST, símbolos, errores y prototipo C/D. |
| 3 | 20% | 29 de noviembre, semana 18 | Síntesis, archivos `.txt`, A–E y validación por destino. |

El PDF no imprime el año junto a estas fechas. El plan usa **2026 como supuesto de calendario de esta sesión**, que debe cotejarse con Aula Digital. Indica grupos de cuatro personas, entrega vía Aula Digital y defensa por videoconferencia programada por el docente. No se inventarán integrantes, carnés ni horarios. Para Fase 2 se recomiendan las clases 13–16 de la unidad 4; para Fase 3, las clases 17–20 de la unidad 5. Ambas actividades estiman 15 días de desarrollo.

## 3. Qué exige cada rúbrica

La meta propuesta es aportar evidencia para el nivel **Estratégico (9–10)**. La nota la decide el docente; tener un checklist completo no garantiza una calificación. Los pesos de cada tabla suman 100% dentro de su fase.

### Fase 1 — continuidad del cierre previo, página 7

| Criterio | Peso | Base exigida | Evidencia para aspirar a Estratégico |
|---|---:|---|---|
| Gramática | 30% | Gramática completa y correcta para el subconjunto definido. | Formalización completa y casos documentados. |
| Destinos | 25% | Tipos y estructuras equivalentes para dos lenguajes. | Comparación completa y justificación técnica sólida. |
| Traducción manual A/B | 30% | Equivalencia correcta en ambos destinos. | Traducciones optimizadas y casos adicionales propuestos, manteniendo los algoritmos oficiales. |
| Documentación | 15% | Documento completo y consistente. | Presentación profesional apta para uso institucional. |

### Fase 2 — página 9

| Criterio | Peso | Base exigida | Evidencia para aspirar a Estratégico |
|---|---:|---|---|
| Analizador léxico | 20% | Reconocer todos los tokens definidos. | Reconocimiento eficiente y reportes claros, con casos especiales. |
| Diseño y comprensión del AST | 20% | AST correcto y explicación de construcción/recorrido. | Eficiencia, recuperación de errores sintácticos y explicación técnica sólida. |
| Semántica y símbolos | 20% | Validaciones principales de tipos y declaración. | Validaciones completas con manejo de ámbitos/scopes. |
| Gestor de errores | 25% | Tipo y línea, incluso en estructuras anidadas. | Errores completos con sugerencias de corrección. |
| Documentación y prototipo C/D | 15% | Funcionamiento con C y D. | Robustez documentada y pruebas más allá de los mínimos; el nivel Destacado pide sus tres casos por programa. |

### Fase 3 — página 11

| Criterio | Peso | Base exigida | Evidencia para aspirar a Estratégico |
|---|---:|---|---|
| Generación desde AST | 20% | Generar recorriendo el AST del subconjunto definido. | Código correcto, idiomático y manejo eficiente de casos complejos. |
| Dos destinos como mínimo | 20% | Generación correcta en ambos. | Más de dos lenguajes **o calidad sobresaliente en ambos**. |
| Arreglos y funciones | 20% | Arreglos 1D y funciones con paso por valor. | Soporte robusto y casos borde; el nivel Destacado incluye validación de límites/índices. |
| Funcionamiento integral A–E | 25% | Procesar entrada `.txt` y producir salidas `.txt` para los cinco programas. | Los cinco programas y sus 15 casos sin fallos, con manejo de errores. |
| Validación por lenguaje | 15% | Ejecutar los casos del anexo en al menos dos lenguajes. | Todos los casos en todos los destinos soportados y evidencia documentada. |

**Decisión de alcance:** mantener Python y JavaScript/Node.js. La rúbrica no obliga a incorporar PHP, Java, C# o C++; son opciones de destino. Tampoco exige BNF y EBNF simultáneamente. Se mantiene EBNF y se explica su notación. Una animación del AST es una posible mejora didáctica; el documento y los diagramas de recorrido sí son exigencias académicas.

## 4. Requerimientos verificables

Los identificadores se utilizan en la matriz y el plan. «Cierre» significa que hay implementación o entregable y evidencia suficiente de aceptación.

### 4.1 Continuidad de Fase 1

| ID | Requerimiento | Criterio de aceptación | Origen |
|---|---|---|---|
| F1-GRAM | Formalizar sintaxis, léxico y tipos. | EBNF, precedencia, nombres Unicode/NFC, números, cadenas/escapes y comentarios coinciden con el lexer/parser; ejemplos válidos e inválidos por familia. Se aclara que entero/decimal son formas de `number`, si se conserva el modelo actual. | p.7 + feedback |
| F1-DEST | Comparar y justificar Python/Node. | Tabla fuente → Python → JavaScript de tipos, operadores, control, arrays, funciones e I/O, con límites de precisión y decisiones propias del compilador. | p.7 + feedback |
| F1-AB | Conservar traducciones manuales A/B comentadas y equivalentes. | Seis datasets en cada destino, stdin en lote e interacción; casos adicionales separados de los oficiales. Cualquier optimización conserva mensajes, lecturas, evaluación y ramas. | p.4, 7 + feedback |
| F1-DOC | Cerrar presentación editorial. | Portada correcta, integrantes confirmados, índice y páginas renderizados y revisados, código legible, comentarios y evidencia de ejecución identificada correctamente. | p.3, 7 + feedback |

### 4.2 Fase 2: análisis y prototipo

| ID | Requerimiento | Criterio de aceptación | Origen |
|---|---|---|---|
| F2-LEX | Analizador léxico real para todo el vocabulario definido. | Tokens con clase, lexema, valor y ubicación; distingue palabras reservadas/identificadores, operadores dobles, comentarios, números y cadenas. Errores léxicos localizados y recuperación acotada. | p.1, 9 |
| F2-AST | Construir y explicar el AST. | Paréntesis, precedencia y anidación correctos; estructura recorrible, spans y ejemplos. Recuperación de varios errores sin ciclos infinitos; un árbol parcial no habilita traducción inválida. Documentar algoritmo y complejidad observada. | p.1, 9 |
| F2-SEM | Validar semántica y mantener símbolos por ámbito. | Tipos, inicialización, nombres, funciones, argumentos, retornos, arrays y scopes comprobados con positivos/negativos. Símbolos muestran nombre, categoría, tipo, ámbito y referencias. Explicar declaración implícita y ámbitos reales, sin atribuir scopes por bloque si no existen. | p.1, 9 |
| F2-ERR | Gestor de errores claro y accionable. | Código, fase, mensaje, línea/columna y sugerencia específica para los errores de usuario cubiertos; UI y exportación coherentes. Probar errores independientes y anidados; bloquear generación cuando corresponda. | p.1, 9 |
| F2-CD | Prototipo funcional con C y D. | Tres casos de C y tres de D, salida en consola y documentación. Para mantener el compromiso del producto: 6 datasets × 2 runtimes = 12 ejecuciones reales. Añadir casos inéditos y límites, con expectativas justificadas. | p.4–5, 9 |
| F2-DOC | Informe y defensa propios de Fase 2. | Diseño del lexer, parser/AST, semántica, tabla de símbolos y gestor de errores; construcción/recorrido explicado con código real; demostración C/D y errores; índice, figuras, pruebas y límites. | p.1, 8–9 |

### 4.3 Fase 3: síntesis, archivos y ejecución

| ID | Requerimiento | Criterio de aceptación | Origen |
|---|---|---|---|
| F3-GEN | Generar desde AST validado. | Cada construcción soportada tiene regla de emisión. Modificar fuente cambia AST/artefactos; código correcto e idiomático; errores bloquean salida ejecutable. Casos complejos conservan semántica. | p.2, 11 |
| F3-DEST | Mantener al menos dos destinos correctos. | Python y JavaScript autónomos, cada uno ejecutado por su runtime. Comparación de resultados; ningún destino se resuelve con respuestas precalculadas. | p.2, 11 |
| F3-ARR | Arreglos 1D y funciones con paso por valor. | Índices/dimensiones válidos, límites, inicialización, funciones, retorno, aridad, scopes y casos borde. El contrato de paso de parámetros debe ser explícito y probado, incluyendo arrays si se aceptan como argumentos. | p.11 |
| F3-IN | Recibir pseudocódigo desde archivo `.txt`. | Cargar cada A–E desde `.txt` real y procesar el contenido vigente. Validar UTF-8, tildes y finales de línea; tratar errores de carga sin perder silenciosamente información. | p.2, 11 |
| F3-ERRTXT | Generar archivo `.txt` con errores de compilación. | Descarga real con diagnósticos léxicos/sintácticos/semánticos, ubicación y sugerencia. Se puede exportar una fuente inválida sin permitir código ejecutable. No basta JSON renombrado. | p.2 |
| F3-CODETXT | Generar un `.txt` de código traducido por destino. | Descargas separadas Python/JavaScript contienen el código completo del artefacto vigente, sin cercas Markdown ni transcripciones de consola. Se comprueba contenido y ejecución tras copiarlo a la extensión del runtime. | p.2, 11 |
| F3-AE | Validar los cinco programas y todos sus casos. | 15 datasets × 2 destinos = 30 ejecuciones reales, resultados oficiales y stdout de consola, inputs, stderr, estado/exit, duración, runtimes y hashes. Si se agregan destinos, se validan también los 15 casos en cada uno. | p.4–6, 11 |
| F3-DOC | Informe final, diagramas y defensa. | Carátula, resumen de análisis de Fase 2, diagrama del recorrido del AST y traducción por destino, lenguajes soportados, instrucciones, archivos y evidencia A–E. Se explica qué parte es programa y qué parte son auxiliares del runtime. | p.2, 10–11 |

### 4.4 Compromisos del producto que siguen vigentes

| ID | Compromiso | Cierre requerido | Procedencia |
|---|---|---|---|
| X-REAL | Evidencia auténtica y vigente. | Diferenciar inspección estática, prueba local, prueba OCI y resultado histórico. Un informe previo no certifica el checkout actual. | Solicitud original y contrato operativo |
| X-HASH | Fuente y artefactos coherentes. | Edición invalida análisis/traducción; exportar y ejecutar siempre corresponde a la fuente vigente. Hashes reproducibles. | Contrato operativo |
| X-SAFE | Ejecutar código de usuario con aislamiento. | OCI rootless o VM comprobada, sin red y con límites; falla explícita si no está disponible. La espera de entrada interactiva no consume el tiempo de cálculo. | Contrato operativo + corrección solicitada previamente |
| X-COMP | Admitir programas inéditos dentro de la gramática. | Pruebas combinadas y negativas para las construcciones soportadas, además de A–E. Toda falla nueva obtiene regresión y corrección de causa. | Solicitud previa sobre próximas fases + nivel Estratégico |

No se añaden despliegue público, nube, cobros ni nuevos lenguajes como condición de estas entregas. La auditoría manual de accesibilidad y la validación multiplataforma del contrato anterior siguen pendientes por separado; la CI remota continúa dispensada por el usuario, sin declararla verificada.

## 5. Contratos de cierre propuestos

Estas decisiones de ingeniería concretan el PDF; nombres de archivos y campos no son una transcripción de la rúbrica.

### 5.1 Intercambio de archivos `.txt`

1. Entrada `programa.txt`: pseudocódigo UTF-8. Probar LF y CRLF; definir el tratamiento de BOM y de una codificación inválida. Cualquier normalización debe ser explícita y coherente con los spans y el hash.
2. Salidas `programa.python.txt` y `programa.javascript.txt`: mismos bytes UTF-8 que el artefacto completo que se descargaría como `.py` o `.js`. Conservar las descargas actuales.
3. Errores `programa.errores.txt`: encabezado con hash de fuente, estado y total; por diagnóstico: severidad, fase, código, línea/columna, mensaje y sugerencia. Conservar el orden de diagnóstico de la API de manera determinista.
4. Una fuente válida puede generar un informe textual `SIN ERRORES DE COMPILACIÓN`; una fuente inválida genera errores y bloquea salidas de código. Los fallos de ejecución se identifican como runtime, no como errores de compilación.
5. API propuesta: ampliar `ExportKind` con `python-txt`, `javascript-txt` y `diagnostics-txt`; integrar el registro de archivos, MIME `text/plain; charset=utf-8`, validaciones y controles UI. No es suficiente cambiar la etiqueta del botón.
6. Un ZIP de entrega puede facilitar el empaquetado, pero no es obligatorio en el PDF ni sustituye las descargas individuales.

### 5.2 Semántica que debe quedar inequívoca

- Entero y decimal: hoy son formas del tipo `number`; Python materializa literales integrales como `int`, mientras JavaScript usa `Number`. La EBNF todavía describe un modelo IEEE-754 común. Resolver esa diferencia de contrato y comprobar aritmética cerca de `2^53`, fracciones, módulo, desbordamiento y representación de salida antes de prometer equivalencia universal.
- Parámetros escalares: asignar al parámetro dentro de una función no cambia la variable del llamador. Documentar retorno, recursión, llamada adelantada y alcance local/global.
- Parámetros array: el código actual emite argumentos directamente, lo que requiere revisar aliasing. Para cumplir una promesa de paso por valor también en arrays aceptados, la decisión propuesta es copiar el arreglo 1D al entrar a la función y probar independencia. No afirmar que ya sucede. Si el docente limita el requisito a escalares, registrar esa aclaración antes de ajustar alcance.
- Índices fuente: `1..n`; dimensiones e índices enteros seguros; errores localizados para cero, negativos, fraccionarios, exceso de rango y elementos sin inicializar.
- No cambiar el algoritmo académico para que un caso adicional produzca otro resultado: por ejemplo D inicializa `max = 0`. Un caso de negativos debe respetar ese algoritmo o pertenecer a un programa inédito con su propia especificación.

### 5.3 Explicación del AST

Ya existe un árbol desplegable. Mejorarlo con nombre/operador/valor/tipo inferido y etiquetas de relaciones (`left`, `right`, `condition`, `body`, etc.) facilita defender la estructura. Esta mejora es una decisión de presentación; el PDF exige comprensión, explicación y diagramas, no una biblioteca gráfica específica.

El informe debe seguir al menos una expresión de A y construcciones de C/D/E desde fuente → nodo → regla de emisión → línea destino. Explicar que los paréntesis condicionan el árbol aunque no necesiten un nodo propio. Usar nodos y mapas reales; un diagrama ilustrativo se identifica como tal.

## 6. Oráculo oficial de aceptación

Los casos observados en las páginas 4–6 coinciden con `examples/official-cases.json`. Se preservan los prompts y el orden de `Leer`. La columna siguiente resume solo las líneas finales; `\n` significa salto de línea, no una barra impresa.

| Caso | Entradas en orden | Salida final oficial |
|---|---|---|
| A-1 | `4, 2, 3` | `El resultado es: 16` |
| A-2 | `10, 5, 2` | `El resultado es: 28` |
| A-3 | `6, 3, 4` | `El resultado es: 34` |
| B-1 | `8, 80` | `Aprobado` |
| B-2 | `7, 60` | `Reprobado por asistencia` |
| B-3 | `4, 90` | `Reprobado por nota` |
| C-1 | `4` | `El factorial es: 24\nLa suma es: 20` |
| C-2 | `5` | `El factorial es: 120\nLa suma es: 30` |
| C-3 | `1` | `El factorial es: 1\nLa suma es: 2` |
| D-1 | `3, 4, 9, 2` | `El promedio es: 5\nEl número mayor es: 9` |
| D-2 | `4, 10, 20, 5, 15` | `El promedio es: 12.5\nEl número mayor es: 20` |
| D-3 | `5, 1, 1, 1, 1, 1` | `El promedio es: 1\nEl número mayor es: 1` |
| E-1 | `5, 4` | `El área es: 20\nClasificación: Pequeña` |
| E-2 | `10, 8` | `El área es: 80\nClasificación: Grande` |
| E-3 | `6, 9` | `El área es: 54\nClasificación: Grande` |

Los separadores `/` entre salidas de algunas tablas del PDF representan dos instrucciones `Escribir`, como confirma el pseudocódigo. Se comparará stdout completo, incluidos prompts; si se normalizan CRLF/LF, conservar también la comparación y salida crudas.

## 7. Definición de terminado

**Fase 2:** informe propio y defensa preparada; diseño verificable de todas las capas de análisis; tokens/AST/símbolos/errores reales; evidencia C/D completa; pruebas adicionales y sugerencias/recuperación para aspirar a Estratégico; sin defectos bloqueantes conocidos en lo presentado.

**Fase 3:** lo anterior más generación desde AST, entrada y salidas `.txt`, errores `.txt`, funciones/arreglos con contrato probado, A–E 30/30 en los dos runtimes aislados, evidencia descargada desde la UI, diagramas por destino, informe final y arranque reproducible.

El cierre global del producto conserva además los pendientes contractuales de [REMAINING_GATES.md](REMAINING_GATES.md). No se hereda el indicador histórico «202/205» como porcentaje de cumplimiento de esta rúbrica nueva.
