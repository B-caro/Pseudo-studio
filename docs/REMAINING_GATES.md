# Verificaciones pendientes para cierre total

El producto y las suites locales están implementados. Estos controles requieren un entorno o una persona que no está disponible en el workspace actual; no se sustituyen con inferencias.

## P9-17 y P12-12 — Auditoría manual WCAG 2.2 AA

La suite automatizada `frontend/e2e/accessibility.spec.ts` ejecuta axe en las siete secciones, comprueba navegación por teclado y termina sin violaciones. Falta una sesión manual con tecnología de asistencia.

1. Inicia la app con `python3.12 scripts/manage.py start` y abre `http://127.0.0.1:5173`.
2. Registra navegador, sistema operativo y lector de pantalla usados.
3. Recorre Editor, Traducción, Consola, Pruebas, Proyectos, Defensa y Ayuda solo con teclado y lector de pantalla.
4. Comprueba nombres/roles/estados anunciados, orden y visibilidad del foco, mensajes de error y cambios de estado, y que los estados no dependan únicamente del color.
5. Mide contraste en texto, controles, estados y foco; adjunta resultados, hallazgos y evidencia visual. Repite los flujos clave en viewport móvil.
6. Corrige todo hallazgo que incumpla WCAG 2.2 AA y repite Playwright axe y la sesión manual antes de marcar ambas tareas.

**Evidencia aceptable:** informe de auditoría con tecnología/versiones, flujos examinados, resultados de teclado/lector/contraste, defectos corregidos y resultado final. La ejecución de axe por sí sola no cierra estas tareas.

## P11-F6 — Ejecución en CI remota

El workflow está definido en `.github/workflows/ci.yml`; `pytest`, build, Playwright, verificación del sandbox, auditorías y 30 casos oficiales se ejecutaron localmente. El checkout no tiene remote Git (`git remote -v` no devuelve entradas). Una búsqueda de solo lectura entre repositorios personales y organizaciones accesibles tampoco encontró un repositorio candidato del proyecto, así que no conecté uno ajeno. El job prepara Docker rootless y configura el perfil AppArmor requerido por Ubuntu 24.04 cuando el kernel informa AppArmor activo; `manage.py verify` rechaza el job si `docker info` no demuestra la frontera. Referencias: [Docker rootless mode](https://docs.docker.com/engine/security/rootless/) y [Ubuntu 24.04 runner image](https://github.com/actions/runner-images).

En este WSL, `/sys/module/apparmor` no está disponible. `apparmor_parser --preprocess` aceptó la estructura del perfil, pero el parser no pudo comprobarla contra el kernel ni cargarla. El workflow debe demostrar este paso en la VM Ubuntu de Actions; el test local no se cuenta como sustituto.

1. Configura el remote del repositorio, por ejemplo `git remote add origin <URL_DEL_REPOSITORIO>`.
2. Publica el commit `2adddeb` o uno posterior a una rama que active `push`/`pull_request`.
3. Ejecuta `.github/workflows/ci.yml` en el runner remoto y conserva URL/ID del workflow, commit asociado y estado final.
4. Descarga y revisa el artefacto `pseudo-studio-acceptance`; debe contener los reportes A–E y evidencia de calidad.

No se necesita una credencial de nube para el producto. Sí se necesita un remote al que el usuario tenga acceso y un runner de GitHub Actions habilitado.

## RNF-10 — Validación nativa fuera de WSL2

La guía de bootstrap cubre Windows/WSL2, macOS y Linux rootless; la ejecución real de este workspace es WSL2 con Docker Desktop VM. Para cerrar la validación multiplataforma, realiza en macOS y/o Linux rootless:

```sh
python3.12 scripts/manage.py bootstrap
python3.12 scripts/manage.py verify
python3.12 scripts/manage.py start
python3.12 scripts/manage.py smoke
.venv/bin/pytest -q
```

Registra sistema, versión de Docker/rootless engine, salida de `verify` y resultados. El runtime debe demostrar rootless o VM Docker Desktop comprobable y ambos runtimes no privilegiados.

### Intento en Ubuntu WSL2 (2026-10-10)

**Actualización posterior:** el usuario reactivó Docker y `manage.py verify` volvió a pasar con `available: true`, frontera `docker-desktop-vm`, Python 3.12.14 y Node v22.22.2 con UID no privilegiado, seccomp, `NoNewPrivs` y cero capabilities. El bloqueo de acceso a Docker descrito a continuación es histórico. El plan reproducible para la nueva suite está en [WSL_TEST_PLAN_AGENT.md](WSL_TEST_PLAN_AGENT.md) y se ejecuta con `bash scripts/validate_wsl.sh`.

El script completo ya se ejecutó sobre `5bce0a1` desde un clon local limpio: 76 tests + 22 subtests, Playwright 6/6, A–E 30/30, smoke y backup correctos, auditorías sin vulnerabilidades y exit 0 en sus 30 etapas. Los hashes y resultados están en `reports/wsl-validation-summary.json`. Se verificó Docker Desktop VM; esta corrida no añade evidencia de Linux rootless, macOS, CI remota ni lector de pantalla manual.

Se comprobó este entorno a petición del usuario: Ubuntu 24.04.1 LTS sobre WSL2, kernel `5.15.153.1-microsoft-standard-WSL2`, systemd activo, usuario `bucaro` con rangos `/etc/subuid` y `/etc/subgid` (100000:65536). `python3.12 scripts/manage.py bootstrap` terminó con exit 1: instaló/validó Python y Node, `npm ci` reportó cero vulnerabilidades y Playwright instaló Chromium, pero el pull de la imagen Python falló porque Docker no está disponible en esta distro. `python3.12 scripts/manage.py verify` terminó con exit 1: `El engine OCI no responde`; `available: false`, `engine_ready: false`, sin frontera de aislamiento ni seccomp. `python3.12 scripts/manage.py smoke` terminó con exit 1 por conexión rechazada a la API, que no estaba iniciada. `.venv/bin/pytest -q` terminó con exit 1: **47 passed, 10 subtests passed, 15 failed, 14 errors**; los errores de integración y fallos de API/runtime reportan el mismo engine OCI no disponible. La integración WSL de Docker Desktop no está activada/disponible en esta distro; el cliente informa “Docker could not be found in this WSL 2 distro”. Tampoco están instalados `dockerd-rootless.sh`, `rootlesskit`, `newuidmap`, `newgidmap` ni `slirp4netns`. El kernel WSL no expone `/sys/module/apparmor`; Docker Desktop con VM y Docker rootless no se pudieron verificar aquí. `sudo -n true` falla (no hay sudo no interactivo), por lo que no se instalaron paquetes ni se modificó el sistema. Para continuar en este WSL: activar la integración de esta distro en Docker Desktop o instalar/configurar Docker Engine rootless con los paquetes `uidmap`, `dbus-user-session` y `slirp4netns`, y volver a ejecutar los cuatro comandos. Esta comprobación no cierra RNF-10.
