# Fuentes y casos oficiales

`A.psc`–`E.psc` reproducen las fuentes visibles en las páginas 3–5 de `Context/fase_1.pdf`. `official-cases.json` conserva los 15 datasets y las salidas finales publicadas en la especificación operativa.

Las entradas se guardan como líneas de texto en el orden de las sentencias `Leer`. El formato `expected_tail` contiene las líneas de resultado de la tabla oficial; los prompts previos forman parte del stdout real y se validarán aparte al ejecutar.

No hay código de destino copiado a mano en estas fixtures. Los artefactos Python/JavaScript se generarán desde el compilador y se registrarán bajo `reports/` cuando los runtimes aislados estén disponibles.
