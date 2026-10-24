# Paquete académico de Fase 3

`fuentes/` contiene A–E como UTF-8 `.txt`; `traducciones/` contiene los artefactos completos generados por el compilador como extensión nativa y como `.txt`. Cada par de destino es byte a byte idéntico. `errores/` contiene una fuente inválida y el diagnóstico real; `evidencia/` incluye fixtures, casos extendidos, reportes y capturas; `documentos/` reúne informes, guiones y matrices.

Para regenerar artefactos desde el repositorio: `python3.12 scripts/build_phase3_package.py`. Para validar el aislamiento y repetir A–E: `python3.12 scripts/manage.py verify` y `python3.12 scripts/run_official_acceptance.py`. Las pruebas ampliadas se repiten con `python3.12 scripts/run_extended_acceptance.py`; suite completa: `.venv/bin/pytest -q`; E2E: `npm --prefix frontend run test:e2e`. La evidencia incluida es la corrida registrada en `evidencia/reportes/`.
