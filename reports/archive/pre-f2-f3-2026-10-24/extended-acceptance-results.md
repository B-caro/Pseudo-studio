# Extended compiler and runtime acceptance

Generated: `2026-10-17T03:47:13.315652+00:00`
Result: **45/45 checks passed**.

The original A–E fixtures are unchanged. These additional programs exercise more combinations of the public language grammar.

## Environment

- OCI isolation boundary: `docker-desktop-vm`
- Python runtime: `3.12.14`
- Node runtime: `v22.22.2`

## Valid programs in both runtimes

| Program / case | Target | Input lines | Status | Exit | Duration ms | Exact stdout | stderr | Source SHA-256 | Artifact SHA-256 |
|---|---|---|---|---:|---:|---|---|---|---|
| X01-recursion-forward-call / factorial-6 | python | `["factorial", "6"]` | completed | 0 | 461.76 | expected `Factorial de 6 = 720\n`, actual `Factorial de 6 = 720\n` | `` | `7ab62e0e70ac7c51fba47819bb28bad23cbb1eba2d2f603ce27136bed98b3e7f` | `0e75a29e7229eca1da99cd23418c803fbfa9d2a17ba6b56f19b701f68c06fecb` |
| X01-recursion-forward-call / factorial-6 | javascript | `["factorial", "6"]` | completed | 0 | 393.30 | expected `Factorial de 6 = 720\n`, actual `Factorial de 6 = 720\n` | `` | `7ab62e0e70ac7c51fba47819bb28bad23cbb1eba2d2f603ce27136bed98b3e7f` | `a94892fdad5410d637c96e6a339e939258b665a3aaa764c502313476ce4d36f0` |
| X01-recursion-forward-call / factorial-base-0 | python | `["factorial", "0"]` | completed | 0 | 441.82 | expected `Factorial de 0 = 1\n`, actual `Factorial de 0 = 1\n` | `` | `7ab62e0e70ac7c51fba47819bb28bad23cbb1eba2d2f603ce27136bed98b3e7f` | `0e75a29e7229eca1da99cd23418c803fbfa9d2a17ba6b56f19b701f68c06fecb` |
| X01-recursion-forward-call / factorial-base-0 | javascript | `["factorial", "0"]` | completed | 0 | 403.39 | expected `Factorial de 0 = 1\n`, actual `Factorial de 0 = 1\n` | `` | `7ab62e0e70ac7c51fba47819bb28bad23cbb1eba2d2f603ce27136bed98b3e7f` | `a94892fdad5410d637c96e6a339e939258b665a3aaa764c502313476ce4d36f0` |
| X01-recursion-forward-call / guard-rejects-mode | python | `["otro", "4"]` | completed | 0 | 447.91 | expected `Entrada no válida\n`, actual `Entrada no válida\n` | `` | `7ab62e0e70ac7c51fba47819bb28bad23cbb1eba2d2f603ce27136bed98b3e7f` | `0e75a29e7229eca1da99cd23418c803fbfa9d2a17ba6b56f19b701f68c06fecb` |
| X01-recursion-forward-call / guard-rejects-mode | javascript | `["otro", "4"]` | completed | 0 | 407.68 | expected `Entrada no válida\n`, actual `Entrada no válida\n` | `` | `7ab62e0e70ac7c51fba47819bb28bad23cbb1eba2d2f603ce27136bed98b3e7f` | `a94892fdad5410d637c96e6a339e939258b665a3aaa764c502313476ce4d36f0` |
| X02-arrays-and-loops / positive-even-count | python | `["4", "-4", "4", "-2", "10"]` | completed | 0 | 463.02 | expected `Promedio=2\nMayor=10\nPares positivos=2\n`, actual `Promedio=2\nMayor=10\nPares positivos=2\n` | `` | `20b7cb6d9dc9f10225fec06725cfa87aed6901a410d411a92be053201038b15f` | `a5945c42857ec45a98c41d68be0edbf1c120a1013cc756bdb4a0c00346d8a054` |
| X02-arrays-and-loops / positive-even-count | javascript | `["4", "-4", "4", "-2", "10"]` | completed | 0 | 410.53 | expected `Promedio=2\nMayor=10\nPares positivos=2\n`, actual `Promedio=2\nMayor=10\nPares positivos=2\n` | `` | `20b7cb6d9dc9f10225fec06725cfa87aed6901a410d411a92be053201038b15f` | `cdc1110b3fd9c387ddba018fa8ed35c10193c6d55d6876dc307b424cc7ae6272` |
| X02-arrays-and-loops / negative-fractional-average | python | `["3", "-8", "-3", "-2"]` | completed | 0 | 462.25 | expected `Promedio=-4.33333333333333\nMayor=-2\nPares positivos=0\n`, actual `Promedio=-4.33333333333333\nMayor=-2\nPares positivos=0\n` | `` | `20b7cb6d9dc9f10225fec06725cfa87aed6901a410d411a92be053201038b15f` | `a5945c42857ec45a98c41d68be0edbf1c120a1013cc756bdb4a0c00346d8a054` |
| X02-arrays-and-loops / negative-fractional-average | javascript | `["3", "-8", "-3", "-2"]` | completed | 0 | 412.67 | expected `Promedio=-4.33333333333333\nMayor=-2\nPares positivos=0\n`, actual `Promedio=-4.33333333333333\nMayor=-2\nPares positivos=0\n` | `` | `20b7cb6d9dc9f10225fec06725cfa87aed6901a410d411a92be053201038b15f` | `cdc1110b3fd9c387ddba018fa8ed35c10193c6d55d6876dc307b424cc7ae6272` |
| X02-step-direction-inclusive-loop / auto-descending-inclusive | python | `["5", "1"]` | completed | 0 | 493.13 | expected `Suma inclusiva=15\n`, actual `Suma inclusiva=15\n` | `` | `08ee791239751e25c06e613175719e25840393d756cb4daf148ada44179b213d` | `ae38c496845986fe4a1d3e50aac4c58fce6a87cf0155c5493bd55081db756709` |
| X02-step-direction-inclusive-loop / auto-descending-inclusive | javascript | `["5", "1"]` | completed | 0 | 466.72 | expected `Suma inclusiva=15\n`, actual `Suma inclusiva=15\n` | `` | `08ee791239751e25c06e613175719e25840393d756cb4daf148ada44179b213d` | `25d9ff0d94e46ea0364e3957e808442249ae6cb1139c528c32edf2e0ac43e06b` |
| X02-step-direction-inclusive-loop / auto-ascending-inclusive | python | `["1", "5"]` | completed | 0 | 505.37 | expected `Suma inclusiva=15\n`, actual `Suma inclusiva=15\n` | `` | `08ee791239751e25c06e613175719e25840393d756cb4daf148ada44179b213d` | `ae38c496845986fe4a1d3e50aac4c58fce6a87cf0155c5493bd55081db756709` |
| X02-step-direction-inclusive-loop / auto-ascending-inclusive | javascript | `["1", "5"]` | completed | 0 | 431.61 | expected `Suma inclusiva=15\n`, actual `Suma inclusiva=15\n` | `` | `08ee791239751e25c06e613175719e25840393d756cb4daf148ada44179b213d` | `25d9ff0d94e46ea0364e3957e808442249ae6cb1139c528c32edf2e0ac43e06b` |
| X02-step-direction-inclusive-loop / auto-single-iteration | python | `["3", "3"]` | completed | 0 | 487.69 | expected `Suma inclusiva=3\n`, actual `Suma inclusiva=3\n` | `` | `08ee791239751e25c06e613175719e25840393d756cb4daf148ada44179b213d` | `ae38c496845986fe4a1d3e50aac4c58fce6a87cf0155c5493bd55081db756709` |
| X02-step-direction-inclusive-loop / auto-single-iteration | javascript | `["3", "3"]` | completed | 0 | 793.85 | expected `Suma inclusiva=3\n`, actual `Suma inclusiva=3\n` | `` | `08ee791239751e25c06e613175719e25840393d756cb4daf148ada44179b213d` | `25d9ff0d94e46ea0364e3957e808442249ae6cb1139c528c32edf2e0ac43e06b` |
| X03-unicode-nested-logic / unicode-and-precedence | python | `["área", "3"]` | completed | 0 | 483.71 | expected `Etiqueta: área / suma: 17\n`, actual `Etiqueta: área / suma: 17\n` | `` | `d75d0be8c1fdd21dc4fab3b0ad207041c26fc3286ec390d7ca4da8894b56ea34` | `2dea94f6d0c968b474e57f872ddef3abdbbf12ab681d855409d6a319fa170b71` |
| X03-unicode-nested-logic / unicode-and-precedence | javascript | `["área", "3"]` | completed | 0 | 442.60 | expected `Etiqueta: área / suma: 17\n`, actual `Etiqueta: área / suma: 17\n` | `` | `d75d0be8c1fdd21dc4fab3b0ad207041c26fc3286ec390d7ca4da8894b56ea34` | `3eac933ae7f4c6e9302309382fa594f3b47446814b812a30a939ec2e5cae59e2` |
| X03-unicode-nested-logic / nested-loop-else-path | python | `["otro", "2"]` | completed | 0 | 468.48 | expected `Etiqueta: otro / suma: 10\n`, actual `Etiqueta: otro / suma: 10\n` | `` | `d75d0be8c1fdd21dc4fab3b0ad207041c26fc3286ec390d7ca4da8894b56ea34` | `2dea94f6d0c968b474e57f872ddef3abdbbf12ab681d855409d6a319fa170b71` |
| X03-unicode-nested-logic / nested-loop-else-path | javascript | `["otro", "2"]` | completed | 0 | 469.01 | expected `Etiqueta: otro / suma: 10\n`, actual `Etiqueta: otro / suma: 10\n` | `` | `d75d0be8c1fdd21dc4fab3b0ad207041c26fc3286ec390d7ca4da8894b56ea34` | `3eac933ae7f4c6e9302309382fa594f3b47446814b812a30a939ec2e5cae59e2` |
| X04-strings-functions-scopes / string-and-even-result | python | `["Ada", "5"]` | completed | 0 | 485.19 | expected `Hola, Ada\nMitad=7\n`, actual `Hola, Ada\nMitad=7\n` | `` | `a10437b6260dff988466937880d53a9f36bb608bfc414d5d52422d0c768f0569` | `2713ea8749fcaacb35563cbd5419f24188b46aa6b5080d2db05135f799c59bb6` |
| X04-strings-functions-scopes / string-and-even-result | javascript | `["Ada", "5"]` | completed | 0 | 425.07 | expected `Hola, Ada\nMitad=7\n`, actual `Hola, Ada\nMitad=7\n` | `` | `a10437b6260dff988466937880d53a9f36bb608bfc414d5d52422d0c768f0569` | `5db64f69ad186f75b4ce843da0b172d50385cb83b1b68824a26b08b41bc9f92a` |
| X04-strings-functions-scopes / empty-string-and-odd-result | python | `["", "4"]` | completed | 0 | 488.40 | expected `Hola, invitado\nResultado=11\n`, actual `Hola, invitado\nResultado=11\n` | `` | `a10437b6260dff988466937880d53a9f36bb608bfc414d5d52422d0c768f0569` | `2713ea8749fcaacb35563cbd5419f24188b46aa6b5080d2db05135f799c59bb6` |
| X04-strings-functions-scopes / empty-string-and-odd-result | javascript | `["", "4"]` | completed | 0 | 440.36 | expected `Hola, invitado\nResultado=11\n`, actual `Hola, invitado\nResultado=11\n` | `` | `a10437b6260dff988466937880d53a9f36bb608bfc414d5d52422d0c768f0569` | `5db64f69ad186f75b4ce843da0b172d50385cb83b1b68824a26b08b41bc9f92a` |

## Invalid source diagnostics

| Case | Passed | Expected diagnostic code/stage/span | Actual diagnostics |
|---|---:|---|---|
| N01-missing-terminator | True | `[{"code": "SYN_UNEXPECTED_TOKEN", "stage": "syntax", "line": 4, "column": 1}, {"code": "SYN_UNEXPECTED_TOKEN", "stage": "syntax", "line": 5, "column": 1}]` | `[{"code": "SYN_UNEXPECTED_TOKEN", "stage": "syntax", "line": 4, "column": 1}, {"code": "SYN_UNEXPECTED_TOKEN", "stage": "syntax", "line": 5, "column": 1}]` |
| N02-undefined-identifier | True | `[{"code": "SEM_UNDEFINED_IDENTIFIER", "stage": "semantic", "line": 2, "column": 10}]` | `[{"code": "SEM_UNDEFINED_IDENTIFIER", "stage": "semantic", "line": 2, "column": 10}]` |
| N03-invalid-condition-type | True | `[{"code": "SEM_TYPE_MISMATCH", "stage": "semantic", "line": 2, "column": 4}]` | `[{"code": "SEM_TYPE_MISMATCH", "stage": "semantic", "line": 2, "column": 4}]` |
| N04-constant-division-by-zero | True | `[{"code": "SEM_DIV_ZERO", "stage": "semantic", "line": 2, "column": 18}]` | `[{"code": "SEM_DIV_ZERO", "stage": "semantic", "line": 2, "column": 18}]` |
| N05-uninitialized-branch-variable | True | `[{"code": "SEM_UNINITIALIZED", "stage": "semantic", "line": 5, "column": 10}]` | `[{"code": "SEM_UNINITIALIZED", "stage": "semantic", "line": 5, "column": 10}]` |
| N06-string-function-wrong-argument-type | True | `[{"code": "SEM_TYPE_MISMATCH", "stage": "semantic", "line": 3, "column": 10}]` | `[{"code": "SEM_TYPE_MISMATCH", "stage": "semantic", "line": 3, "column": 10}]` |

## Controlled runtime failures

| Case | Target | Inputs | Expected error | Actual status / exit / error | Diagnostic line | Duration ms | Source SHA-256 | Artifact SHA-256 |
|---|---|---|---|---|---:|---:|---|---|
| R01-division-by-zero | python | `["0"]` | RUN_DIV_ZERO | runtime_error / 70 / `RUN_DIV_ZERO` | 3 | 476.68 | `1dbcbba4e396abb2d5ec17a0bb0ec9a4c00eca14e084b418a5b56a1cc0cb5b43` | `3e466385c5230ceffc2e813285318c2fdf7062e24f94b6d5ba060ca80ea0c630` |
| R01-division-by-zero | javascript | `["0"]` | RUN_DIV_ZERO | runtime_error / 70 / `RUN_DIV_ZERO` | 3 | 437.58 | `1dbcbba4e396abb2d5ec17a0bb0ec9a4c00eca14e084b418a5b56a1cc0cb5b43` | `c6192080d1028bfdf2887316d98d743518958db27f2b38f14a9ea79c35e81059` |
| R02-array-bounds | python | `["3"]` | RUN_BOUNDS | runtime_error / 70 / `RUN_BOUNDS` | 4 | 455.46 | `6970a878275fdd962bcd3f8cd201c14928c23b08d1f1c4eb3e37968c79521e66` | `c1d32f79fc1d5f8cf69c1039476090239f5d090a346628b1d50a5365d6674601` |
| R02-array-bounds | javascript | `["3"]` | RUN_BOUNDS | runtime_error / 70 / `RUN_BOUNDS` | 4 | 417.44 | `6970a878275fdd962bcd3f8cd201c14928c23b08d1f1c4eb3e37968c79521e66` | `7ce0ece8a82732e7fad7835950b4eedc94b31778e22b2110ed8615a2cf83dcfa` |
| R03-uninitialized-array-value | python | `[]` | RUN_UNINITIALIZED | runtime_error / 70 / `RUN_UNINITIALIZED` | 3 | 447.17 | `53a886a06ab43839910e91b1114c8d298e19a17729835f65fb0651fba0fa9242` | `dfba5c868eca1bde3e89ef8fab0f0a6fad2976ef7da868b16fb056f27d52c990` |
| R03-uninitialized-array-value | javascript | `[]` | RUN_UNINITIALIZED | runtime_error / 70 / `RUN_UNINITIALIZED` | 3 | 405.93 | `53a886a06ab43839910e91b1114c8d298e19a17729835f65fb0651fba0fa9242` | `efb3ffaf1eb6739caba8c7ca1086ab9495d3382d5366da43f1044711b6ac4c5e` |
| R04-invalid-dynamic-dimension | python | `["0"]` | RUN_INVALID_DIMENSION | runtime_error / 70 / `RUN_INVALID_DIMENSION` | 3 | 456.41 | `d3b2cb0c607ab6712dd428d6b846cf9c362e3ef0ed2e821faf360b285cb39b05` | `4d5b2a31358c0f6b701217763b24b09eb72e226828e576ba13afd502f562b1a7` |
| R04-invalid-dynamic-dimension | javascript | `["0"]` | RUN_INVALID_DIMENSION | runtime_error / 70 / `RUN_INVALID_DIMENSION` | 3 | 409.94 | `d3b2cb0c607ab6712dd428d6b846cf9c362e3ef0ed2e821faf360b285cb39b05` | `05b19120e21ed84be7d45c4fb859fe7dec7b60618603fbad84f3d109ceb9669d` |
| R05-invalid-numeric-input | python | `["abc"]` | RUN_INPUT_INVALID | runtime_error / 70 / `RUN_INPUT_INVALID` | 2 | 466.29 | `ebd67d2079eb7704d2a76438a39ff9325d2c780bc8b7cebd0db8fce2d97acb6a` | `603efc5fafa537e8ff3c234fd113f2b2c28446b08ae3a2ea07e564b70c12493f` |
| R05-invalid-numeric-input | javascript | `["abc"]` | RUN_INPUT_INVALID | runtime_error / 70 / `RUN_INPUT_INVALID` | 2 | 413.48 | `ebd67d2079eb7704d2a76438a39ff9325d2c780bc8b7cebd0db8fce2d97acb6a` | `52b154fa10cb2586e456e8140e3567a623f006dee9cd20b62bee504391aceb28` |

## Coverage summary

- Valid executions: 24/24.
- Invalid programs diagnosed at expected spans: 6/6.
- Runtime errors normalized across Python and Node: 10/10.
- Features covered: forward and recursive functions, return aliases, parameter typing, strings and Unicode, nested conditionals and loops, precedence, booleans, modulo, negative and fractional arithmetic, dynamic arrays, 1-based bounds, uninitialized values, malformed input, and located diagnostics.
