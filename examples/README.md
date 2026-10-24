# Fuentes y casos oficiales

`A.psc`–`E.psc` reproducen las fuentes visibles en las páginas 3–5 de `Context/fase_1.pdf`. `official-cases.json` conserva los 15 datasets y las salidas finales publicadas en la especificación operativa.

Las entradas se guardan como líneas de texto en el orden de las sentencias `Leer`. El formato `expected_tail` contiene las líneas de resultado de la tabla oficial; los prompts previos forman parte del stdout real y se validarán aparte al ejecutar.

No hay código de destino copiado a mano en estas fixtures. Los artefactos Python/JavaScript se generarán desde el compilador y se registrarán bajo `reports/` cuando los runtimes aislados estén disponibles.

## Traducciones manuales comentadas de Fase 1

`phase1-translations/` contiene versiones manuales de A y B en Python y JavaScript. Mantienen los algoritmos de `A.psc` y `B.psc`, agregan comentarios didácticos y leen stdin línea por línea. En JavaScript esto conserva las entradas siguientes aunque el evaluador entregue el lote completo antes de iniciar el proceso.

Repite la verificación de los seis datasets A/B en ambos runtimes con entradas agrupadas: `python3.12 scripts/run_phase1_manual_acceptance.py` y `.venv/bin/pytest -q backend/tests/test_phase1_manual_translations.py`.
