# Verificaciones pendientes para cierre total

El producto y las suites locales están implementados. La auditoría WCAG manual y la cobertura de otras plataformas aún requieren evidencia específica. El usuario dispensó la ejecución CI remota; esa casilla se deja sin verificar y fuera de los gates de entrega.

## P9-17 y P12-12 — Auditoría manual WCAG 2.2 AA

La suite automatizada `frontend/e2e/accessibility.spec.ts` ejecuta axe en las siete secciones, comprueba navegación por teclado y termina sin violaciones. Falta una sesión manual con tecnología de asistencia.

1. Inicia la app con `python3.12 scripts/manage.py start` y abre `http://127.0.0.1:5173`.
2. Registra navegador, sistema operativo y lector de pantalla usados.
3. Recorre Editor, Traducción, Consola, Pruebas, Proyectos, Defensa y Ayuda solo con teclado y lector de pantalla.
4. Comprueba nombres/roles/estados anunciados, orden y visibilidad del foco, mensajes de error y cambios de estado, y que los estados no dependan únicamente del color.
5. Mide contraste en texto, controles, estados y foco; adjunta resultados, hallazgos y evidencia visual. Repite los flujos clave en viewport móvil.
6. Corrige todo hallazgo que incumpla WCAG 2.2 AA y repite Playwright axe y la sesión manual antes de marcar ambas tareas.

**Evidencia aceptable:** informe de auditoría con tecnología/versiones, flujos examinados, resultados de teclado/lector/contraste, defectos corregidos y resultado final. La ejecución de axe por sí sola no cierra estas tareas.

## P11-F6 — CI remota dispensada; tarea sin verificar

El usuario decidió que la ejecución CI se puede descartar. El repositorio público `https://github.com/B-caro/Pseudo-studio.git` quedó publicado en `main` en `a472179`; el workflow sigue versionado y un push puede iniciarlo automáticamente. No se espera ni se usa el resultado de Actions como criterio de aceptación. P11-F6 sigue sin verificar: las 30 etapas locales aprobadas no prueban ejecución remota.

WSL no expone `/sys/module/apparmor`; el perfil solo se preprocesó, no se validó/cargó en el kernel. Este límite se conserva como evidencia histórica y no se intenta completar porque la ejecución remota quedó dispensada.

No marcar P11-F6 `[x]` ni atribuir una ejecución remota sin artefactos. La definición del workflow se mantiene en el repo para quien decida ejecutarla después.

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

El workspace principal también quedó iniciado para la auditoría: API `ready` y frontend HTTP 200 en los puertos locales 8000/5173; smoke Python/Node exit 0. Detalle: `reports/wsl-workspace-smoke.json`.

Se comprobó este entorno a petición del usuario: Ubuntu 24.04.1 LTS sobre WSL2, kernel `5.15.153.1-microsoft-standard-WSL2`, systemd activo, usuario `bucaro` con rangos `/etc/subuid` y `/etc/subgid` (100000:65536). `python3.12 scripts/manage.py bootstrap` terminó con exit 1: instaló/validó Python y Node, `npm ci` reportó cero vulnerabilidades y Playwright instaló Chromium, pero el pull de la imagen Python falló porque Docker no está disponible en esta distro. `python3.12 scripts/manage.py verify` terminó con exit 1: `El engine OCI no responde`; `available: false`, `engine_ready: false`, sin frontera de aislamiento ni seccomp. `python3.12 scripts/manage.py smoke` terminó con exit 1 por conexión rechazada a la API, que no estaba iniciada. `.venv/bin/pytest -q` terminó con exit 1: **47 passed, 10 subtests passed, 15 failed, 14 errors**; los errores de integración y fallos de API/runtime reportan el mismo engine OCI no disponible. La integración WSL de Docker Desktop no está activada/disponible en esta distro; el cliente informa “Docker could not be found in this WSL 2 distro”. Tampoco están instalados `dockerd-rootless.sh`, `rootlesskit`, `newuidmap`, `newgidmap` ni `slirp4netns`. El kernel WSL no expone `/sys/module/apparmor`; Docker Desktop con VM y Docker rootless no se pudieron verificar aquí. `sudo -n true` falla (no hay sudo no interactivo), por lo que no se instalaron paquetes ni se modificó el sistema. Para continuar en este WSL: activar la integración de esta distro en Docker Desktop o instalar/configurar Docker Engine rootless con los paquetes `uidmap`, `dbus-user-session` y `slirp4netns`, y volver a ejecutar los cuatro comandos. Esta comprobación no cierra RNF-10.
