# Estado de evidencia de ejecución

Paquete generado desde el compilador actual. A–E conserva las fuentes oficiales; los 10 artefactos de Python y JavaScript se generan con `compile_source`. Los pares `.py/.js` y `.txt` son byte a byte idénticos. Este paquete incluye casos extendidos, reportes de runtime y capturas del navegador.

- A–E: **30/30** ejecuciones OCI reales, fecha `2026-10-24T07:28:34.337374+00:00`.
- Casos extendidos/negativos/runtime: **54/54** checks, fecha `2026-10-24T07:27:55.621203+00:00`.
- Runtime: Docker Desktop VM (`docker-desktop-vm`), Python `3.12.14`, Node `v22.22.2`; controles y cuotas en los JSON incluidos.
- Validación completa, limitaciones y hashes: `reportes/` y `docs/VALIDATION_REPORT.md` del repositorio.

La frontera Docker Desktop VM está verificada; no se presenta el daemon como rootless. La auditoría manual con lector de pantalla, pruebas nativas macOS/Linux rootless, CI remota dispensada por el usuario y render final del DOCX aún no están certificadas.
