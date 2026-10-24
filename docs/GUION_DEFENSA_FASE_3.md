# Guion de defensa — Fase 3

## Preparación

Arranca API y frontend con `python3.12 scripts/manage.py start`, verifica `python3.12 scripts/manage.py verify` y abre `http://127.0.0.1:5173`. Para ejecutar, la interfaz debe indicar **Sandbox verificado**. Prepara `A.txt`–`E.txt` desde `examples/` (o desde `delivery/fase-3/fuentes/` si el paquete fue generado) y conserva los originales.

## Demostración

| Paso y click | Qué explicar |
|---|---|
| 1. En **Editor**, pulsa **Abrir archivo** y carga `A.txt`. Pulsa **◎ Analizar** y muestra Tokens y AST. | “El contenido del archivo pasa a ser la fuente activa. Se decodifica como UTF-8, se quita un BOM inicial y se conserva el texto con sus saltos de línea. El hash y los tokens corresponden al contenido cargado.” |
| 2. Abre **Traducción** y pulsa **Traducir fuente actual**. | “Los dos programas se generan recorriendo el mismo AST validado. El archivo completo incluye los auxiliares que necesitan entrada, salida y control de errores.” |
| 3. En el panel Python, descarga `.py` y **Python .txt**; luego en el panel JavaScript descarga `.js` y **JavaScript .txt**. | “Los TXT de código son archivos de texto portables: contienen los mismos bytes que cada artefacto nativo completo. No son un resumen ni una transcripción del resultado.” |
| 4. Ejecuta Python y JavaScript desde **Consola**, usando las entradas de A. | “La API entrega el artefacto al runner aislado. Python y Node leen stdin y escriben stdout reales dentro del límite local; la aplicación no ejecuta el código del usuario dentro del proceso API.” |
| 5. Abre **Pruebas**, selecciona A y pulsa **Ejecutar A en ambos destinos**. Expande un caso; repite para B–E. | “Cada programa conserva sus tres entradas oficiales. La matriz compara el stdout exacto y registra estado, exit code, duración y hashes. Quince casos por dos destinos producen treinta ejecuciones.” |
| 6. Regresa al editor e introduce `Escribir @`. Pulsa **Analizar**, luego **Errores → Exportar errores .txt**. | “Los errores de compilación también tienen un archivo TXT legible con fase, código, línea, columna y sugerencia. Un error permite obtener el reporte, pero el botón de código no puede generar un artefacto ejecutable.” |
| 7. Corrige la fuente y pulsa **Analizar** otra vez. Edita después un carácter para mostrar el estado desactualizado. | “Cada cambio de fuente invalida el resultado previo. Primero analizo otra vez; así no descargo ni ejecuto una compilación anterior como si fuera la actual.” |

## Cierre sugerido

“En Fase 3 el mismo árbol se traduce a dos lenguajes y cada artefacto corre en su runtime. A–E comprueba las reglas en programas académicos distintos; los casos adicionales comprueban funciones, arreglos, errores y bordes. Los archivos TXT permiten intercambiar la fuente, el código completo y los errores, conservando hashes para relacionar lo que se ve con lo que se ejecuta.”

No se declara el gate de 30/30 hasta que la corrida aislada genere los registros de esta misma versión. Ver el estado y las limitaciones en [INFORME_FASE_3.md](INFORME_FASE_3.md).
