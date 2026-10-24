# Extended compiler and runtime acceptance

Generated: `2026-10-24T07:27:55.621203+00:00`
Result: **54/54 checks passed**.

The original A–E fixtures are unchanged. These additional programs exercise more combinations of the public language grammar.

## Environment

- OCI isolation boundary: `docker-desktop-vm`
- Python runtime: `3.12.14`
- Node runtime: `v22.22.2`

## Valid programs in both runtimes

| Program / case | Target | Input lines | Status | Exit | Duration ms | Exact stdout | stderr | Source SHA-256 | Artifact SHA-256 |
|---|---|---|---|---:|---:|---|---|---|---|
| X01-recursion-forward-call / factorial-6 | python | `["factorial", "6"]` | completed | 0 | 620.00 | expected `Factorial de 6 = 720\n`, actual `Factorial de 6 = 720\n` | `` | `7ab62e0e70ac7c51fba47819bb28bad23cbb1eba2d2f603ce27136bed98b3e7f` | `9abc7ca494b450158866bf179d94acb91b2904720f88a352eee3ae5d4e0494a8` |
| X01-recursion-forward-call / factorial-6 | javascript | `["factorial", "6"]` | completed | 0 | 569.19 | expected `Factorial de 6 = 720\n`, actual `Factorial de 6 = 720\n` | `` | `7ab62e0e70ac7c51fba47819bb28bad23cbb1eba2d2f603ce27136bed98b3e7f` | `9a5168e72c191b7a5e958534ebcc0c2806b0e3899e756e2c6feefebd6053b85f` |
| X01-recursion-forward-call / factorial-base-0 | python | `["factorial", "0"]` | completed | 0 | 603.71 | expected `Factorial de 0 = 1\n`, actual `Factorial de 0 = 1\n` | `` | `7ab62e0e70ac7c51fba47819bb28bad23cbb1eba2d2f603ce27136bed98b3e7f` | `9abc7ca494b450158866bf179d94acb91b2904720f88a352eee3ae5d4e0494a8` |
| X01-recursion-forward-call / factorial-base-0 | javascript | `["factorial", "0"]` | completed | 0 | 613.14 | expected `Factorial de 0 = 1\n`, actual `Factorial de 0 = 1\n` | `` | `7ab62e0e70ac7c51fba47819bb28bad23cbb1eba2d2f603ce27136bed98b3e7f` | `9a5168e72c191b7a5e958534ebcc0c2806b0e3899e756e2c6feefebd6053b85f` |
| X01-recursion-forward-call / guard-rejects-mode | python | `["otro", "4"]` | completed | 0 | 617.11 | expected `Entrada no válida\n`, actual `Entrada no válida\n` | `` | `7ab62e0e70ac7c51fba47819bb28bad23cbb1eba2d2f603ce27136bed98b3e7f` | `9abc7ca494b450158866bf179d94acb91b2904720f88a352eee3ae5d4e0494a8` |
| X01-recursion-forward-call / guard-rejects-mode | javascript | `["otro", "4"]` | completed | 0 | 525.21 | expected `Entrada no válida\n`, actual `Entrada no válida\n` | `` | `7ab62e0e70ac7c51fba47819bb28bad23cbb1eba2d2f603ce27136bed98b3e7f` | `9a5168e72c191b7a5e958534ebcc0c2806b0e3899e756e2c6feefebd6053b85f` |
| X02-arrays-and-loops / positive-even-count | python | `["4", "-4", "4", "-2", "10"]` | completed | 0 | 619.48 | expected `Promedio=2\nMayor=10\nPares positivos=2\n`, actual `Promedio=2\nMayor=10\nPares positivos=2\n` | `` | `20b7cb6d9dc9f10225fec06725cfa87aed6901a410d411a92be053201038b15f` | `7efaf2de6149409d511362d99e30653e2545956a44959c7693a397a8fb67489a` |
| X02-arrays-and-loops / positive-even-count | javascript | `["4", "-4", "4", "-2", "10"]` | completed | 0 | 630.82 | expected `Promedio=2\nMayor=10\nPares positivos=2\n`, actual `Promedio=2\nMayor=10\nPares positivos=2\n` | `` | `20b7cb6d9dc9f10225fec06725cfa87aed6901a410d411a92be053201038b15f` | `d0175e72384c2b0ab36476eccbfd172465d77f27b15d97db2f419777fd946453` |
| X02-arrays-and-loops / negative-fractional-average | python | `["3", "-8", "-3", "-2"]` | completed | 0 | 584.94 | expected `Promedio=-4.33333333333333\nMayor=-2\nPares positivos=0\n`, actual `Promedio=-4.33333333333333\nMayor=-2\nPares positivos=0\n` | `` | `20b7cb6d9dc9f10225fec06725cfa87aed6901a410d411a92be053201038b15f` | `7efaf2de6149409d511362d99e30653e2545956a44959c7693a397a8fb67489a` |
| X02-arrays-and-loops / negative-fractional-average | javascript | `["3", "-8", "-3", "-2"]` | completed | 0 | 575.43 | expected `Promedio=-4.33333333333333\nMayor=-2\nPares positivos=0\n`, actual `Promedio=-4.33333333333333\nMayor=-2\nPares positivos=0\n` | `` | `20b7cb6d9dc9f10225fec06725cfa87aed6901a410d411a92be053201038b15f` | `d0175e72384c2b0ab36476eccbfd172465d77f27b15d97db2f419777fd946453` |
| X02-step-direction-inclusive-loop / auto-descending-inclusive | python | `["5", "1"]` | completed | 0 | 646.16 | expected `Suma inclusiva=15\n`, actual `Suma inclusiva=15\n` | `` | `08ee791239751e25c06e613175719e25840393d756cb4daf148ada44179b213d` | `bb65339091c825cf58cf4bcd6f82f049d44f1b9ad985c4cd89fd90e9834e08db` |
| X02-step-direction-inclusive-loop / auto-descending-inclusive | javascript | `["5", "1"]` | completed | 0 | 559.28 | expected `Suma inclusiva=15\n`, actual `Suma inclusiva=15\n` | `` | `08ee791239751e25c06e613175719e25840393d756cb4daf148ada44179b213d` | `e98df68d9e17380cd3edac34256047fd76dcdc2f705fe63148a56fcfc9285852` |
| X02-step-direction-inclusive-loop / auto-ascending-inclusive | python | `["1", "5"]` | completed | 0 | 662.49 | expected `Suma inclusiva=15\n`, actual `Suma inclusiva=15\n` | `` | `08ee791239751e25c06e613175719e25840393d756cb4daf148ada44179b213d` | `bb65339091c825cf58cf4bcd6f82f049d44f1b9ad985c4cd89fd90e9834e08db` |
| X02-step-direction-inclusive-loop / auto-ascending-inclusive | javascript | `["1", "5"]` | completed | 0 | 714.36 | expected `Suma inclusiva=15\n`, actual `Suma inclusiva=15\n` | `` | `08ee791239751e25c06e613175719e25840393d756cb4daf148ada44179b213d` | `e98df68d9e17380cd3edac34256047fd76dcdc2f705fe63148a56fcfc9285852` |
| X02-step-direction-inclusive-loop / auto-single-iteration | python | `["3", "3"]` | completed | 0 | 879.78 | expected `Suma inclusiva=3\n`, actual `Suma inclusiva=3\n` | `` | `08ee791239751e25c06e613175719e25840393d756cb4daf148ada44179b213d` | `bb65339091c825cf58cf4bcd6f82f049d44f1b9ad985c4cd89fd90e9834e08db` |
| X02-step-direction-inclusive-loop / auto-single-iteration | javascript | `["3", "3"]` | completed | 0 | 746.57 | expected `Suma inclusiva=3\n`, actual `Suma inclusiva=3\n` | `` | `08ee791239751e25c06e613175719e25840393d756cb4daf148ada44179b213d` | `e98df68d9e17380cd3edac34256047fd76dcdc2f705fe63148a56fcfc9285852` |
| X03-unicode-nested-logic / unicode-and-precedence | python | `["área", "3"]` | completed | 0 | 675.89 | expected `Etiqueta: área / suma: 17\n`, actual `Etiqueta: área / suma: 17\n` | `` | `d75d0be8c1fdd21dc4fab3b0ad207041c26fc3286ec390d7ca4da8894b56ea34` | `537b0db66f486d91c04f17ff26cc7f776cf79282a1db179b71bf4cdb640f5121` |
| X03-unicode-nested-logic / unicode-and-precedence | javascript | `["área", "3"]` | completed | 0 | 671.39 | expected `Etiqueta: área / suma: 17\n`, actual `Etiqueta: área / suma: 17\n` | `` | `d75d0be8c1fdd21dc4fab3b0ad207041c26fc3286ec390d7ca4da8894b56ea34` | `cd609e592b634e888cb6b63cefd1ea99ebcafd2928da077eed656e1f732679e9` |
| X03-unicode-nested-logic / nested-loop-else-path | python | `["otro", "2"]` | completed | 0 | 635.05 | expected `Etiqueta: otro / suma: 10\n`, actual `Etiqueta: otro / suma: 10\n` | `` | `d75d0be8c1fdd21dc4fab3b0ad207041c26fc3286ec390d7ca4da8894b56ea34` | `537b0db66f486d91c04f17ff26cc7f776cf79282a1db179b71bf4cdb640f5121` |
| X03-unicode-nested-logic / nested-loop-else-path | javascript | `["otro", "2"]` | completed | 0 | 587.66 | expected `Etiqueta: otro / suma: 10\n`, actual `Etiqueta: otro / suma: 10\n` | `` | `d75d0be8c1fdd21dc4fab3b0ad207041c26fc3286ec390d7ca4da8894b56ea34` | `cd609e592b634e888cb6b63cefd1ea99ebcafd2928da077eed656e1f732679e9` |
| X04-strings-functions-scopes / string-and-even-result | python | `["Ada", "5"]` | completed | 0 | 619.47 | expected `Hola, Ada\nMitad=7\n`, actual `Hola, Ada\nMitad=7\n` | `` | `a10437b6260dff988466937880d53a9f36bb608bfc414d5d52422d0c768f0569` | `0563485ab92aacb19789810f71b489a87610d6077831483b20acd63ca7255692` |
| X04-strings-functions-scopes / string-and-even-result | javascript | `["Ada", "5"]` | completed | 0 | 557.83 | expected `Hola, Ada\nMitad=7\n`, actual `Hola, Ada\nMitad=7\n` | `` | `a10437b6260dff988466937880d53a9f36bb608bfc414d5d52422d0c768f0569` | `0cddad6859a2d69d9bf688f138f0e1ee6441099f6873aaac8b341e6b68d21b8b` |
| X04-strings-functions-scopes / empty-string-and-odd-result | python | `["", "4"]` | completed | 0 | 687.10 | expected `Hola, invitado\nResultado=11\n`, actual `Hola, invitado\nResultado=11\n` | `` | `a10437b6260dff988466937880d53a9f36bb608bfc414d5d52422d0c768f0569` | `0563485ab92aacb19789810f71b489a87610d6077831483b20acd63ca7255692` |
| X04-strings-functions-scopes / empty-string-and-odd-result | javascript | `["", "4"]` | completed | 0 | 536.91 | expected `Hola, invitado\nResultado=11\n`, actual `Hola, invitado\nResultado=11\n` | `` | `a10437b6260dff988466937880d53a9f36bb608bfc414d5d52422d0c768f0569` | `0cddad6859a2d69d9bf688f138f0e1ee6441099f6873aaac8b341e6b68d21b8b` |
| X05-sort-search-array-function / sort-and-find-final-value | python | `["5", "4", "1", "3", "5", "2", "5"]` | completed | 0 | 640.50 | expected `Ordenados:\n1\n2\n3\n4\n5\nPosición=5\n`, actual `Ordenados:\n1\n2\n3\n4\n5\nPosición=5\n` | `` | `8ee67075c207b7dd61a7965808873934d61478d0f728a54565ab44c768c45757` | `a7a593116b3d2b97f75ae3109f35e51c0577406014d7356a679d937964b6a915` |
| X05-sort-search-array-function / sort-and-find-final-value | javascript | `["5", "4", "1", "3", "5", "2", "5"]` | completed | 0 | 684.24 | expected `Ordenados:\n1\n2\n3\n4\n5\nPosición=5\n`, actual `Ordenados:\n1\n2\n3\n4\n5\nPosición=5\n` | `` | `8ee67075c207b7dd61a7965808873934d61478d0f728a54565ab44c768c45757` | `36dd145cb0f850d043c891722b0f2d4a1097ff187af9fa7e28d58c72144a9f0c` |
| X05-sort-search-array-function / sort-duplicates-and-missing-value | python | `["4", "-1", "7", "0", "7", "3"]` | completed | 0 | 622.88 | expected `Ordenados:\n-1\n0\n7\n7\nPosición=0\n`, actual `Ordenados:\n-1\n0\n7\n7\nPosición=0\n` | `` | `8ee67075c207b7dd61a7965808873934d61478d0f728a54565ab44c768c45757` | `a7a593116b3d2b97f75ae3109f35e51c0577406014d7356a679d937964b6a915` |
| X05-sort-search-array-function / sort-duplicates-and-missing-value | javascript | `["4", "-1", "7", "0", "7", "3"]` | completed | 0 | 532.90 | expected `Ordenados:\n-1\n0\n7\n7\nPosición=0\n`, actual `Ordenados:\n-1\n0\n7\n7\nPosición=0\n` | `` | `8ee67075c207b7dd61a7965808873934d61478d0f728a54565ab44c768c45757` | `36dd145cb0f850d043c891722b0f2d4a1097ff187af9fa7e28d58c72144a9f0c` |

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
| R01-division-by-zero | python | `["0"]` | RUN_DIV_ZERO | runtime_error / 70 / `RUN_DIV_ZERO` | 3 | 629.37 | `1dbcbba4e396abb2d5ec17a0bb0ec9a4c00eca14e084b418a5b56a1cc0cb5b43` | `d4aff0ca985f7c60de246ebdb214d0fa2d68973149bf8e6d83ee478e4caa91bd` |
| R01-division-by-zero | javascript | `["0"]` | RUN_DIV_ZERO | runtime_error / 70 / `RUN_DIV_ZERO` | 3 | 547.20 | `1dbcbba4e396abb2d5ec17a0bb0ec9a4c00eca14e084b418a5b56a1cc0cb5b43` | `94c17b110f48e531613206d7da414c3d78d93fd1125aa807a3e028c2fcf2eb64` |
| R02-array-bounds | python | `["3"]` | RUN_BOUNDS | runtime_error / 70 / `RUN_BOUNDS` | 4 | 616.97 | `6970a878275fdd962bcd3f8cd201c14928c23b08d1f1c4eb3e37968c79521e66` | `f2d3074973bf6459e76aa1155a6dda60388041c9bdf4afc03ae7f5a55c923820` |
| R02-array-bounds | javascript | `["3"]` | RUN_BOUNDS | runtime_error / 70 / `RUN_BOUNDS` | 4 | 551.74 | `6970a878275fdd962bcd3f8cd201c14928c23b08d1f1c4eb3e37968c79521e66` | `0997fc2d8a4f77a691896721d86e8eaa0d97636a19032bdfb12cc46255d56e8c` |
| R03-uninitialized-array-value | python | `[]` | RUN_UNINITIALIZED | runtime_error / 70 / `RUN_UNINITIALIZED` | 3 | 667.32 | `53a886a06ab43839910e91b1114c8d298e19a17729835f65fb0651fba0fa9242` | `19e66b8c836f919faf29660cec2f6b564c1e5a18361c4eb5a0e31dc88f1ea65a` |
| R03-uninitialized-array-value | javascript | `[]` | RUN_UNINITIALIZED | runtime_error / 70 / `RUN_UNINITIALIZED` | 3 | 531.47 | `53a886a06ab43839910e91b1114c8d298e19a17729835f65fb0651fba0fa9242` | `a7edfaaec3e540434b605881ef0473c1b3e01b1df6e6d0da4f247298a0bc5719` |
| R04-zero-dynamic-dimension | python | `["0"]` | RUN_INVALID_DIMENSION | runtime_error / 70 / `RUN_INVALID_DIMENSION` | 3 | 575.93 | `d3b2cb0c607ab6712dd428d6b846cf9c362e3ef0ed2e821faf360b285cb39b05` | `c5d7f9c9be314b3066dfe735715a1c2f0322759ee447105b2faf20bc16aee8a2` |
| R04-zero-dynamic-dimension | javascript | `["0"]` | RUN_INVALID_DIMENSION | runtime_error / 70 / `RUN_INVALID_DIMENSION` | 3 | 564.53 | `d3b2cb0c607ab6712dd428d6b846cf9c362e3ef0ed2e821faf360b285cb39b05` | `db86dc80f72f912dc9c9dc670f9fd9edea39bd43739189cfdf5c23c61e477f9e` |
| R06-negative-dynamic-dimension | python | `["-1"]` | RUN_INVALID_DIMENSION | runtime_error / 70 / `RUN_INVALID_DIMENSION` | 3 | 614.15 | `d3b2cb0c607ab6712dd428d6b846cf9c362e3ef0ed2e821faf360b285cb39b05` | `c5d7f9c9be314b3066dfe735715a1c2f0322759ee447105b2faf20bc16aee8a2` |
| R06-negative-dynamic-dimension | javascript | `["-1"]` | RUN_INVALID_DIMENSION | runtime_error / 70 / `RUN_INVALID_DIMENSION` | 3 | 558.46 | `d3b2cb0c607ab6712dd428d6b846cf9c362e3ef0ed2e821faf360b285cb39b05` | `db86dc80f72f912dc9c9dc670f9fd9edea39bd43739189cfdf5c23c61e477f9e` |
| R05-invalid-numeric-input | python | `["abc"]` | RUN_INPUT_INVALID | runtime_error / 70 / `RUN_INPUT_INVALID` | 2 | 647.26 | `ebd67d2079eb7704d2a76438a39ff9325d2c780bc8b7cebd0db8fce2d97acb6a` | `23e6bef9eed677e367fc622a88b1036ad7b726f38ce33242ca970b784ef8861a` |
| R05-invalid-numeric-input | javascript | `["abc"]` | RUN_INPUT_INVALID | runtime_error / 70 / `RUN_INPUT_INVALID` | 2 | 593.65 | `ebd67d2079eb7704d2a76438a39ff9325d2c780bc8b7cebd0db8fce2d97acb6a` | `493994cccf063c43deb84fd7f1e61e04e2266d9d77b26f99c92cd60be0200d0f` |
| R07-nonfinite-operation | python | `[]` | RUN_NONFINITE | runtime_error / 70 / `RUN_NONFINITE` | 3 | 657.89 | `7994cfac83c2530563f0a6922822c978704bdcc385726546ac8516183c4b7fd4` | `d3b9848bd85db17794d5b640a35efa5073186f7f199632176e2ebe8ca3da499c` |
| R07-nonfinite-operation | javascript | `[]` | RUN_NONFINITE | runtime_error / 70 / `RUN_NONFINITE` | 3 | 586.00 | `7994cfac83c2530563f0a6922822c978704bdcc385726546ac8516183c4b7fd4` | `cee24836c8272e1e5903ec612327876c2c73538e398803b3465b6290acaf60a5` |

## Coverage summary

- Valid executions: 28/28.
- Invalid programs diagnosed at expected spans: 6/6.
- Runtime errors normalized across Python and Node: 14/14.
- Features covered: forward and recursive functions, return aliases, parameter typing, strings and Unicode, nested conditionals and loops, precedence, booleans, modulo, negative and fractional arithmetic, dynamic arrays, 1-based bounds, uninitialized values, malformed input, and located diagnostics.
