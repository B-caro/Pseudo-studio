# Pseudo / Studio — entrega de validación automática a otro agente

## Estado comprobado al preparar esta guía

- Repositorio: `/home/bucaro/.t3/projects/automatas`.
- Docker vuelve a responder desde Ubuntu WSL: servidor 28.1.1, Docker Desktop, kernel WSL2 `5.15.153.1-microsoft-standard-WSL2`.
- Python del host: 3.12.3; Node: 22.22.2; npm: 10.9.7.
- `python3.12 scripts/manage.py verify`: exit 0, `available: true`, frontera `docker-desktop-vm`. Python 3.12.14 y Node v22.22.2 pasan UID 10001, `NoNewPrivs`, seccomp y cero capabilities. Esto verifica la alternativa VM; no certifica un daemon rootless.
- Los puertos 8000/5173 estaban libres. `docker ps` vacío significa que no hay contenedores activos; es normal entre ejecuciones efímeras.
- 202/205 casillas registradas; P9-17/P12-12 (WCAG manual), P11-F6 (CI remota) y RNF-10 (cobertura de plataformas) siguen pendientes.
- El procedimiento completo se ejecutó sobre `5bce0a1`: 30 etapas con exit 0, 76 tests + 22 subtests, cero fallos/errores/skips, cobertura de líneas de backend 89,82 %, Playwright 6/6 sin reintentos y A–E 30/30. Smoke, backup, build y auditorías pasan; cero vulnerabilidades. Evidencia y hashes: `reports/wsl-validation-summary.json`; corrida `reports/runs/wsl-20261010T175319Z-z0u3ep/`. Cada corrida posterior debe medir sus propios resultados.

## Instrucción que puede recibir el agente

> Trabaja en `/home/bucaro/.t3/projects/automatas`. Lee esta guía, `docs/IMPLEMENTATION_STATUS.md`, `docs/TRACEABILITY.md`, `docs/DECISIONS.md` y los documentos de `Context/`. Docker está accesible y el preflight del sandbox pasó. Ejecuta `bash scripts/validate_wsl.sh` desde WSL y revisa cada evidencia. El script valida el HEAD comprometido en una copia local limpia; conserva el original, `Context/`, proyectos y reportes anteriores. Si falla, diagnostica el primer paso fallido, corrige la causa en el repositorio original cuando sea código, prueba la corrección, crea un commit y repite la validación completa sobre ese commit. No cambies salidas oficiales, snapshots ni controles del sandbox para ocultar fallos. No omitas tests. Actualiza trazabilidad y estado solo con evidencia de la corrida nueva. No publiques a un remote sin repositorio y autorización del usuario. La revisión manual WCAG queda a cargo del usuario y no se sustituye por axe.

## Ejecución automática

```bash
cd /home/bucaro/.t3/projects/automatas
bash scripts/validate_wsl.sh
```

El script requiere cambios rastreados ya comprometidos. `Context/` sin rastrear puede permanecer así. Usa un clon local de HEAD; las dependencias se reinstalan sin copiar `.venv`, `node_modules`, `.env` ni datos de la aplicación. Los reportes históricos de ese clon se trasladan a `historical-reports/`, y las nuevas salidas se generan desde cero. Se conserva la configuración del cliente Docker que permite conectar con el daemon; las variables `PSEUDO_STUDIO_*` se fijan a los valores de prueba en el proceso hijo. Se necesitan descargas de PyPI/npm/registro OCI, pero no credenciales de nube ni publicación.

El `origin` de ese clon apunta al filesystem local; no es un repositorio remoto de CI y no cierra P11-F6.

Si los puertos 8000/5173 están ocupados, el script termina antes de arrancar servicios. Identifica su propietario; no mates procesos ajenos. Si pertenecen al `manage.py` del workspace original, puedes detenerlos con `python3.12 scripts/manage.py stop` y repetir. Playwright administra sus propios servidores con `CI=1`, sin reutilización ni reintentos; el smoke se ejecuta después de que esos servidores terminen, usando `start → smoke → backup → stop`.

Todas las suites se ejecutan secuencialmente para no distorsionar tiempos y cuotas del sandbox. El script termina ante el primer error y conserva el log y código de salida; un fallo no se transforma en éxito. No instala paquetes del sistema, no cambia Docker ni necesita sudo. Si faltan bibliotecas del navegador, registra la dependencia y solicita que se instalen los requisitos que indique Playwright antes de repetir; no silencies ese error.

## Etapas y criterios de aprobación

| Orden | Prueba real | Debe demostrar |
|---|---|---|
| 1 | Inventario, Docker, puertos, clon de HEAD y versiones | Commit exacto, WSL identificado, daemon accesible, puertos libres y copia nueva. |
| 2 | `manage.py bootstrap` | Instalación desde lockfiles, Chromium e imágenes por digest; exit 0. |
| 3 | `manage.py verify` | `available: true`, ambos runtimes y controles internos pasan. Si falla, detener pruebas dependientes del runner. |
| 4 | pre-commit, Ruff lint/formato | Cero errores; ningún arreglo automático sin revisar. Si un hook cambia fuentes, corregir/committear en el original y reiniciar. |
| 5 | Suite completa `pytest`, JUnit y cobertura | Cero fallos/errores; revisar que no haya skips o xfails inesperados. Incluye compilador, semántica, API/WS, proyectos, seguridad, límites y diferenciales. |
| 6 | A–E CLI y validación del JSON | Exactamente 15 casos × 2 targets distintos = 30/30; stdout oficial, stderr vacío, exit 0, inputs, estado, duración, versiones y hashes. |
| 7 | Benchmark de 100/1.000 líneas | Percentiles medidos y entorno en JSON/Markdown; contrastar con RNF-12, no confundir emisión del reporte con cumplimiento de la meta. |
| 8 | `npm run build` | TypeScript y build de producción sin errores. |
| 9 | Playwright completo, 1 worker y 0 retries | Los seis tests actuales pasan: editor, análisis, traducción, descargas, consola batch/interactiva, cancelación, pruebas, proyectos, persistencia, siete paneles, teclado/axe y móvil. El panel de pruebas también ejecuta A–E. |
| 10 | `start → smoke → backup → stop` | API/frontend reales en loopback; Python/Node imprimen `OK=42`; backup íntegro de la base de prueba; puertos liberados al terminar. |
| 11 | pip-audit / npm audit | Comandos sin errores y revisión de todos los hallazgos. `npm audit --audit-level=moderate` puede pasar con hallazgos de severidad baja; no reportar cero sin leer el JSON. |
| 12 | Integridad de fuentes y SHA-256 de evidencias | Ningún cambio en fuentes/fixtures causado por la suite; hashes de reportes y evidencia de navegador. |

El script comprueba los códigos de salida y los 30 registros oficiales. El agente debe revisar cobertura, benchmark, skips, auditorías y trazabilidad antes de declarar aceptación; un exit 0 del script no completa las verificaciones humanas/remotas.

## Evidencia y revisión final

Cada ejecución imprime su ruta `reports/runs/wsl-<fecha UTC>-<id>/` y conserva:

- `source-commit.txt`: commit que se probó.
- `stages.tsv`: código de salida y fecha de cada paso ejecutado.
- `exit-code.txt`: resultado final del script; si el proceso fue terminado abruptamente y falta este archivo, la corrida está incompleta.
- `logs/`: stdout/stderr por etapa, Docker, versiones y limpieza en caso de fallo.
- `workspace/reports/`: JUnit, cobertura, A–E JSON/Markdown, benchmark, auditorías, backup y `SHA256SUMS`.
- `workspace/frontend/playwright-report/` y `test-results/`: reporte HTML, resultados y trazas/capturas de fallos.
- `historical-reports/`: evidencia previa, que no se debe contar como salida de esta corrida.

La carpeta de corridas está ignorada por Git. Para la entrega, copiar solo reportes revisados y un resumen a las rutas versionadas pertinentes; no añadir el clon completo, `.venv`, `node_modules`, bases de usuario ni logs con secretos. Conservar los fallos previos y las correcciones/commits que los resuelven.

Tras la suite, comprobar `docker ps -a --filter name=pseudo-studio --format '{{.ID}} {{.Status}} {{.Names}}'`: no debe haber restos atribuibles a esta corrida. Documentar cualquier fuga y corregir la limpieza; no usar `docker system prune` ni borrar contenedores ajenos. La copia limpia se apaga al terminar. Para la revisión manual, iniciar el workspace original con `python3.12 scripts/manage.py start` y ejecutar su `smoke`. En la sesión actual ya se verificaron API `ready` y frontend HTTP 200; están activos en `http://127.0.0.1:5173` y `http://127.0.0.1:8000/api/v1/docs`.

## Lo que sigue después de una corrida local aprobada

1. Actualizar `docs/IMPLEMENTATION_STATUS.md`, `docs/TRACEABILITY.md`, `docs/VALIDATION_REPORT.md` y `docs/REMAINING_GATES.md`, conservando fechas y distinción entre resultados históricos y actuales. Crear commit de evidencia e informar su hash y el commit de código probado.
2. P9-17/P12-12: esperar el informe manual del usuario sobre lector de pantalla, contraste y siete paneles; corregir hallazgos y repetir comprobaciones. Axe no cierra esta parte.
3. P11-F6: cuando el usuario indique un repositorio autorizado, ejecutar el workflow y registrar URL/ID, commit y artefactos. La corrida local no equivale a una ejecución de GitHub Actions.
4. RNF-10: registrar esta evidencia como Windows/Ubuntu WSL2 + Docker Desktop VM. Las validaciones Linux rootless y macOS necesitan sus propios entornos y resultados; no afirmar que WSL las prueba.

Formato de reporte del agente:

```text
Hito: P13; tareas verificadas: <n>/205
Commit probado: <hash>; commit de correcciones/evidencia: <hash>
Entorno y frontera OCI: <versiones; rootless o Docker Desktop VM>
pytest: <resultado real>; cobertura: <porcentaje y alcance>
Playwright: <resultado real>; A–E: <resultado>/30
Smoke/backup/auditorías/benchmark: <resultado real>
Evidencia: <ruta de corrida y hashes>
Servicios activos: <solo los comprobados>
Pendientes humanos/remotos y siguiente acción: <detalle>
```
