# A/B manual translation acceptance

Generated: **2026-10-24T07:11:24.273046+00:00**
Result: **12/12 runs passed**.

- Python: Python 3.12.3
- Node: v22.22.2
- Input delivery: all case lines are written to stdin together in one batch.
- This host run does not claim OCI isolation; the sandbox status is recorded separately.

| Case | Target | Input batch | Exit | Duration ms | Exact stdout | stderr | Source SHA-256 |
|---|---|---|---:|---:|---|---|---|
| A-1 | python | ["4", "2", "3"] | 0 | 17.46 | expected Ingrese el primer número:\nIngrese el segundo número:\nIngrese el tercer número:\nEl resultado es: 16\n, actual Ingrese el primer número:\nIngrese el segundo número:\nIngrese el tercer número:\nEl resultado es: 16\n |  | cbac813510d644757f5cb2ac512b4042d0a37b41959d13379064925b3a74c142 |
| A-1 | javascript | ["4", "2", "3"] | 0 | 20.01 | expected Ingrese el primer número:\nIngrese el segundo número:\nIngrese el tercer número:\nEl resultado es: 16\n, actual Ingrese el primer número:\nIngrese el segundo número:\nIngrese el tercer número:\nEl resultado es: 16\n |  | c33d809cb0ae3676b66c3480d7080309775e3346624befb0df2463b0049d915a |
| A-2 | python | ["10", "5", "2"] | 0 | 21.82 | expected Ingrese el primer número:\nIngrese el segundo número:\nIngrese el tercer número:\nEl resultado es: 28\n, actual Ingrese el primer número:\nIngrese el segundo número:\nIngrese el tercer número:\nEl resultado es: 28\n |  | cbac813510d644757f5cb2ac512b4042d0a37b41959d13379064925b3a74c142 |
| A-2 | javascript | ["10", "5", "2"] | 0 | 22.46 | expected Ingrese el primer número:\nIngrese el segundo número:\nIngrese el tercer número:\nEl resultado es: 28\n, actual Ingrese el primer número:\nIngrese el segundo número:\nIngrese el tercer número:\nEl resultado es: 28\n |  | c33d809cb0ae3676b66c3480d7080309775e3346624befb0df2463b0049d915a |
| A-3 | python | ["6", "3", "4"] | 0 | 22.22 | expected Ingrese el primer número:\nIngrese el segundo número:\nIngrese el tercer número:\nEl resultado es: 34\n, actual Ingrese el primer número:\nIngrese el segundo número:\nIngrese el tercer número:\nEl resultado es: 34\n |  | cbac813510d644757f5cb2ac512b4042d0a37b41959d13379064925b3a74c142 |
| A-3 | javascript | ["6", "3", "4"] | 0 | 21.18 | expected Ingrese el primer número:\nIngrese el segundo número:\nIngrese el tercer número:\nEl resultado es: 34\n, actual Ingrese el primer número:\nIngrese el segundo número:\nIngrese el tercer número:\nEl resultado es: 34\n |  | c33d809cb0ae3676b66c3480d7080309775e3346624befb0df2463b0049d915a |
| B-1 | python | ["8", "80"] | 0 | 22.51 | expected Ingrese su nota final:\nIngrese su porcentaje de asistencia:\nAprobado\n, actual Ingrese su nota final:\nIngrese su porcentaje de asistencia:\nAprobado\n |  | a9679451fa6bb2766554a7f74f24ea2c5398a75a617e812afe9c7f4c8abe0fe8 |
| B-1 | javascript | ["8", "80"] | 0 | 25.13 | expected Ingrese su nota final:\nIngrese su porcentaje de asistencia:\nAprobado\n, actual Ingrese su nota final:\nIngrese su porcentaje de asistencia:\nAprobado\n |  | e7a6b2a628da47b45e3cb7ff9fc26c6be7f7b07db149470b714f7a22f3a6de8f |
| B-2 | python | ["7", "60"] | 0 | 18.76 | expected Ingrese su nota final:\nIngrese su porcentaje de asistencia:\nReprobado por asistencia\n, actual Ingrese su nota final:\nIngrese su porcentaje de asistencia:\nReprobado por asistencia\n |  | a9679451fa6bb2766554a7f74f24ea2c5398a75a617e812afe9c7f4c8abe0fe8 |
| B-2 | javascript | ["7", "60"] | 0 | 21.52 | expected Ingrese su nota final:\nIngrese su porcentaje de asistencia:\nReprobado por asistencia\n, actual Ingrese su nota final:\nIngrese su porcentaje de asistencia:\nReprobado por asistencia\n |  | e7a6b2a628da47b45e3cb7ff9fc26c6be7f7b07db149470b714f7a22f3a6de8f |
| B-3 | python | ["4", "90"] | 0 | 17.75 | expected Ingrese su nota final:\nIngrese su porcentaje de asistencia:\nReprobado por nota\n, actual Ingrese su nota final:\nIngrese su porcentaje de asistencia:\nReprobado por nota\n |  | a9679451fa6bb2766554a7f74f24ea2c5398a75a617e812afe9c7f4c8abe0fe8 |
| B-3 | javascript | ["4", "90"] | 0 | 19.92 | expected Ingrese su nota final:\nIngrese su porcentaje de asistencia:\nReprobado por nota\n, actual Ingrese su nota final:\nIngrese su porcentaje de asistencia:\nReprobado por nota\n |  | e7a6b2a628da47b45e3cb7ff9fc26c6be7f7b07db149470b714f7a22f3a6de8f |
