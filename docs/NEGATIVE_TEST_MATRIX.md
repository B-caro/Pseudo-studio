# Casos negativos N-01..N-12

La matriz procede de la sección 8.1 de `Context/Pseudo_Studio_Requerimientos_v2_Operativo.md`. Los resultados de compilación se comprueban con diagnósticos reales y los casos runtime ejecutan Python/Node en OCI; no se simulan stdout ni códigos de salida.

| Caso | Cobertura automatizada | Resultado afirmado por el test |
|---|---|---|
| N-01 | `test_lexer.py::test_bad_characters_and_unterminated_strings_are_diagnostics`; `test_compiler_service.py::test_invalid_source_has_diagnostics_and_no_artifacts` | `LEX_INVALID_CHAR`, span exacto y cero artefactos. |
| N-02 | `test_language_conformance.py::test_syntax_errors_are_located_and_do_not_emit_ast_as_valid`; `test_compiler_service.py::test_invalid_source_has_diagnostics_and_no_artifacts` | Paréntesis sin cierre da diagnóstico sintáctico y no genera código. |
| N-03 | `test_semantic.py::test_unknown_name_and_read_before_initialization_are_diagnosed` | Símbolo no definido queda localizado por semántica. |
| N-04 | `test_parser.py::test_missing_block_terminator_reports_syntax_error_and_returns` | `FinSi` faltante produce diagnóstico sin bloquear la recuperación. |
| N-05 | `test_semantic.py::test_duplicate_function_names_are_rejected_with_semantic_diagnostic` y `test_type_mismatch_constant_step_zero_and_function_arity` | Nombre de función duplicado, aridad incorrecta y `Paso 0` constante se rechazan en compilación. |
| N-06 | `test_runner_integration.py::test_arrays_are_one_based_and_bounds_errors_are_controlled` | `a[0]` y `a[4]` para dimensión 3 fallan con `RUN_BOUNDS` en ambos destinos; dimensión 0 no compila. |
| N-07 | `test_runner_integration.py::test_runtime_division_and_input_errors_are_normalized` | División entre cero real produce `RUN_DIV_ZERO` en ambos destinos. |
| N-08 | `test_runner_integration.py::test_runtime_division_and_input_errors_are_normalized` y `test_missing_numeric_input_is_controlled_for_both_targets` | Input `NaN` da `RUN_INPUT_INVALID`; EOF da `RUN_INPUT_MISSING`; ambos en Python y Node. |
| N-09 | `test_type_mismatch_constant_step_zero_and_function_arity` y `test_dynamic_zero_step_is_rejected_at_runtime_for_both_targets` | Paso constante cero se previene en semántica; cero leído dinámicamente da `RUN_INVALID_STEP` en ambos runtimes. |
| N-10 | `test_runner_integration.py::test_timeout_and_output_limit_terminate_real_containers`, `test_parallel_sessions_and_manual_cancellation_are_isolated` y `test_api.py::test_interactive_idle_input_expires_and_returns_timeout` | Bucle infinito termina por timeout/cancelación real; espera interactiva sin respuesta termina por timeout. |
| N-11 | `test_runner_integration.py::test_text_input_is_data_and_not_evaluated` y `test_containers_cannot_read_host_files_or_open_network_connections` | Texto tipo `__import__/touch` se conserva como dato; red, archivos del host y socket OCI quedan bloqueados. |
| N-12 | `test_runner_integration.py::test_parallel_sessions_and_manual_cancellation_are_isolated`, `test_concurrency_quota_rejects_excess_run_and_releases_slot_after_cancel` y `test_api.py::test_websocket_disconnect_kills_container_and_releases_session` | Sesión cancelada/desconectada limpia contenedor y slot; otra ejecución saludable concluye sin daño. |

Ejecución: `.venv/bin/pytest -q backend/tests/test_lexer.py backend/tests/test_parser.py backend/tests/test_semantic.py backend/tests/test_compiler_service.py backend/tests/test_runner_integration.py backend/tests/test_api.py`. La suite global añade fixtures académicos, snapshots, comparador diferencial, property tests y UI. El cierre ambiental de CI remota/lector de pantalla está separado en `docs/IMPLEMENTATION_STATUS.md`.
