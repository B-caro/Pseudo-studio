import concurrent.futures
import hashlib
import json
import tempfile
import time
import unittest
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from backend.compiler.service import compile_source
from backend.runtime.runner import OciRunner, RunnerBusy
from backend.test_service.official import official_stdout


class OciRunnerIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = OciRunner(timeout_seconds=5.0)
        controls = cls.runner.verify_controls()
        if not controls["available"]:
            raise RuntimeError(f"Secure OCI runtime is required for these integration tests: {controls}")

    def _run(
        self, source: str, inputs: list[str], target: str, runner: OciRunner | None = None, run_id: str | None = None
    ):
        compiled = compile_source(source)
        self.assertTrue(compiled.translatable, [item.to_dict() for item in compiled.diagnostics])
        artifact = compiled.artifacts[target]
        return (runner or self.runner).run_batch(
            target, artifact.source, inputs, compiled.source_hash, artifact.artifact_hash, run_id
        )

    def test_engine_must_prove_rootless_or_docker_desktop_linux_vm_boundary(self) -> None:
        self.assertEqual(
            OciRunner._isolation_boundary(
                {"SecurityOptions": ["name=seccomp,profile=builtin", "name=rootless"], "KernelVersion": "Linux"}
            ),
            "rootless-oci",
        )
        for kernel in ("6.12.24-linuxkit", "5.15.153.1-microsoft-standard-WSL2"):
            self.assertEqual(
                OciRunner._isolation_boundary({"OperatingSystem": "Docker Desktop", "KernelVersion": kernel}),
                "docker-desktop-vm",
            )
        self.assertIsNone(OciRunner._isolation_boundary({"OperatingSystem": "Ubuntu", "KernelVersion": "Linux"}))

    def test_real_python_and_node_batch_input_and_output(self) -> None:
        source = 'Inicio\nLeer numero\nEscribir "Resultado: ", numero + 1\nFin\n'
        for target in ("python", "javascript"):
            result = self._run(source, ["41"], target)
            self.assertEqual(
                (result.status, result.exit_code, result.stdout, result.stderr), ("completed", 0, "Resultado: 42\n", "")
            )

    def test_runtime_division_and_input_errors_are_normalized(self) -> None:
        division = "Inicio\nLeer divisor\nresultado = 10 / divisor\nEscribir resultado\nFin\n"
        invalid_input = "Inicio\nLeer dato\nEscribir dato\nFin\n"
        for target in ("python", "javascript"):
            div_result = self._run(division, ["0"], target)
            self.assertEqual(
                (div_result.status, div_result.error_code, div_result.exit_code), ("runtime_error", "RUN_DIV_ZERO", 70)
            )
            input_result = self._run(invalid_input, ["NaN"], target)
            self.assertEqual(
                (input_result.status, input_result.error_code, input_result.exit_code),
                ("runtime_error", "RUN_INPUT_INVALID", 70),
            )

    def test_missing_numeric_input_is_controlled_for_both_targets(self) -> None:
        source = "Inicio\nLeer dato\nEscribir dato\nFin\n"
        for target in ("python", "javascript"):
            result = self._run(source, [], target)
            self.assertEqual(
                (result.status, result.error_code, result.exit_code), ("runtime_error", "RUN_INPUT_MISSING", 70)
            )

    def test_dynamic_zero_step_is_rejected_at_runtime_for_both_targets(self) -> None:
        source = "Inicio\nLeer incremento\nPara i = 1 Hasta 3 Paso incremento Hacer\nEscribir i\nFinPara\nFin\n"
        compiled = compile_source(source)
        self.assertTrue(compiled.translatable, [item.to_dict() for item in compiled.diagnostics])
        for target in ("python", "javascript"):
            artifact = compiled.artifacts[target]
            result = self.runner.run_batch(target, artifact.source, ["0"], compiled.source_hash, artifact.artifact_hash)
            self.assertEqual(
                (result.status, result.error_code, result.exit_code), ("runtime_error", "RUN_INVALID_STEP", 70)
            )

    def test_arrays_are_one_based_and_bounds_errors_are_controlled(self) -> None:
        for index in (0, 4):
            source = f"Inicio\nDimension datos[3]\nEscribir datos[{index}]\nFin\n"
            for target in ("python", "javascript"):
                result = self._run(source, [], target)
                self.assertEqual((result.status, result.error_code), ("runtime_error", "RUN_BOUNDS"))
                runtime_error = next(
                    line for line in result.stderr.splitlines() if line.startswith("PSEUDO_RUNTIME_ERROR ")
                )
                self.assertEqual(json.loads(runtime_error.removeprefix("PSEUDO_RUNTIME_ERROR "))["line"], 3)
        invalid_dimension = compile_source("Inicio\nDimension datos[0]\nFin\n")
        self.assertFalse(invalid_dimension.translatable)
        self.assertTrue(invalid_dimension.diagnostics)

    def test_official_condition_and_zero_loop_boundaries_match_both_targets(self) -> None:
        examples_dir = Path(__file__).resolve().parents[2] / "examples"
        cases = [
            ("B", ["6", "75"], "Aprobado"),
            ("B", ["6", "74"], "Reprobado por asistencia"),
            ("C", ["0"], "El factorial es: 0\nLa suma es: 2"),
        ]
        for program, inputs, expected_tail in cases:
            source = (examples_dir / f"{program}.psc").read_text(encoding="utf-8")
            expected = official_stdout(program, inputs, expected_tail)
            for target in ("python", "javascript"):
                with self.subTest(program=program, inputs=inputs, target=target):
                    result = self._run(source, inputs, target)
                    self.assertEqual(
                        (result.status, result.exit_code, result.stdout, result.stderr), ("completed", 0, expected, "")
                    )

    def test_three_new_programs_match_across_both_runtimes(self) -> None:
        programs = [
            (
                """Inicio
Dimension valores[2]
valores[1] = -5
valores[2] = 2
i = 1
suma = 0
Mientras i <= 2 Hacer
    suma = suma + valores[i]
    i = i + 1
FinMientras
Escribir "M=", Resto(suma, 2)
Funcion Resto(numero, divisor)
    Retornar numero Modulo divisor
FinFuncion
Fin
""",
                "M=-1\n",
            ),
            (
                """Inicio
Escribir "F=", Factorial(5)
Funcion Factorial(n)
    Si n <= 1 Entonces
        Retornar 1
    Sino
        Retornar n * Factorial(n - 1)
    FinSi
FinFuncion
Fin
""",
                "F=120\n",
            ),
            (
                """Inicio
Dimension acum[3]
Para i = 1 Hasta 3 Hacer
    acum[i] = i * 2
FinPara
j = 1
total = 0
Mientras j <= 3 Hacer
    total = total + acum[j]
    j = j + 1
FinMientras
Escribir "S=", Ajustar(total)
Funcion Ajustar(x)
    Retornar x + 1
FinFuncion
Fin
""",
                "S=13\n",
            ),
        ]
        for source, expected in programs:
            for target in ("python", "javascript"):
                with self.subTest(target=target, expected=expected):
                    result = self._run(source, [], target)
                    self.assertEqual(
                        (result.status, result.exit_code, result.stdout, result.stderr), ("completed", 0, expected, "")
                    )

    def test_timeout_and_output_limit_terminate_real_containers(self) -> None:
        infinite = "Inicio\ni = 0\nMientras Verdadero Hacer\ni = i + 1\nFinMientras\nFin\n"
        short_runner = OciRunner(timeout_seconds=0.7)
        timed = self._run(infinite, [], "python", short_runner)
        self.assertEqual((timed.status, timed.error_code), ("timed_out", "RUN_TIMEOUT"))

        output = 'Inicio\nMientras Verdadero Hacer\nEscribir "salida repetida"\nFinMientras\nFin\n'
        limited_runner = OciRunner(timeout_seconds=5.0, output_limit=1024)
        limited = self._run(output, [], "javascript", limited_runner)
        self.assertEqual((limited.status, limited.error_code), ("output_limited", "RUN_OUTPUT_LIMIT"))
        self.assertLessEqual(len(limited.stdout.encode()) + len(limited.stderr.encode()), 1024)

    def test_parallel_sessions_and_manual_cancellation_are_isolated(self) -> None:
        infinite = "Inicio\ni = 0\nMientras Verdadero Hacer\ni = i + 1\nFinMientras\nFin\n"
        quick = 'Inicio\nEscribir "sana"\nFin\n'
        compiled = compile_source(infinite)
        artifact = compiled.artifacts["python"]
        run_id = "cancel-session-001"
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            canceled_future = pool.submit(
                self.runner.run_batch,
                "python",
                artifact.source,
                [],
                compiled.source_hash,
                artifact.artifact_hash,
                run_id,
            )
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                with self.runner._active_lock:
                    active = run_id in self.runner._active
                if active:
                    break
                time.sleep(0.02)
            self.assertTrue(active, "El contenedor de cancelación no llegó a iniciarse.")
            self.assertTrue(self.runner.cancel(run_id))
            healthy_future = pool.submit(self._run, quick, [], "javascript")
            canceled = canceled_future.result(timeout=8)
            healthy = healthy_future.result(timeout=8)
        self.assertEqual((canceled.status, canceled.error_code), ("cancelled", "RUN_CANCELLED"))
        self.assertEqual((healthy.status, healthy.exit_code, healthy.stdout), ("completed", 0, "sana\n"))

    def test_concurrency_quota_rejects_excess_run_and_releases_slot_after_cancel(self) -> None:
        limited = OciRunner(timeout_seconds=5.0, max_concurrent_runs=1)
        source = "Inicio\ni = 0\nMientras Verdadero Hacer\ni = i + 1\nFinMientras\nFin\n"
        compiled = compile_source(source)
        artifact = compiled.artifacts["python"]
        run_id = "quota-session-001"
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            active_future = pool.submit(
                limited.run_batch,
                "python",
                artifact.source,
                [],
                compiled.source_hash,
                artifact.artifact_hash,
                run_id,
            )
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                with limited._active_lock:
                    active = run_id in limited._active
                if active:
                    break
                time.sleep(0.02)
            self.assertTrue(active)
            with self.assertRaises(RunnerBusy):
                limited.run_batch("javascript", artifact.source, [], compiled.source_hash, artifact.artifact_hash)
            self.assertTrue(limited.cancel(run_id))
            self.assertEqual(active_future.result(timeout=8).status, "cancelled")
        quick = self._run('Inicio\nEscribir "slot libre"\nFin\n', [], "javascript", limited)
        self.assertEqual((quick.status, quick.stdout), ("completed", "slot libre\n"))

    def test_text_input_is_data_and_not_evaluated(self) -> None:
        source = "Inicio\nLeerTexto payload\nEscribir payload\nFin\n"
        with tempfile.TemporaryDirectory(prefix="pseudo-shell-probe-") as directory:
            marker = Path(directory) / "should-not-exist"
            payload = f"__import__('os').system('touch {marker}')"
            result = self._run(source, [payload], "python")
            self.assertEqual((result.status, result.exit_code, result.stdout), ("completed", 0, payload + "\n"))
            self.assertFalse(marker.exists())

    def test_containers_cannot_read_host_files_or_open_network_connections(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pseudo-host-secret-") as host_directory:
            secret_path = Path(host_directory) / "secret.txt"
            secret_path.write_text("host-only-secret", encoding="utf-8")
            probes = {
                "python": f"""import os, socket
try:
    open({str(secret_path)!r}, encoding="utf-8").read()
    print("HOST_FILE_READ")
except OSError:
    print("HOST_FILE_BLOCKED")
print("ENGINE_SOCKET_PRESENT=" + str(os.path.exists("/var/run/docker.sock")))
try:
    socket.create_connection(("1.1.1.1", 80), timeout=0.5)
    print("NETWORK_ALLOWED")
except OSError:
    print("NETWORK_BLOCKED")
""",
                "javascript": f"""const fs = require("node:fs");
const net = require("node:net");
try {{ fs.readFileSync({json.dumps(str(secret_path))}, "utf8"); console.log("HOST_FILE_READ"); }}
catch {{ console.log("HOST_FILE_BLOCKED"); }}
console.log("ENGINE_SOCKET_PRESENT=" + fs.existsSync("/var/run/docker.sock"));
const socket = net.connect(80, "1.1.1.1");
socket.setTimeout(500);
socket.on("connect", () => {{ console.log("NETWORK_ALLOWED"); socket.destroy(); process.exitCode = 2; }});
socket.on("error", () => {{ console.log("NETWORK_BLOCKED"); }});
socket.on("timeout", () => {{ console.log("NETWORK_BLOCKED"); socket.destroy(); }});
""",
            }
            for target, source in probes.items():
                result = self.runner.run_batch(
                    target,
                    source,
                    [],
                    "security-probe",
                    hashlib.sha256(source.encode("utf-8")).hexdigest(),
                )
                self.assertEqual((result.status, result.exit_code), ("completed", 0), result.stderr)
                self.assertIn("HOST_FILE_BLOCKED", result.stdout)
                socket_status = (
                    "ENGINE_SOCKET_PRESENT=false" if target == "javascript" else "ENGINE_SOCKET_PRESENT=False"
                )
                self.assertIn(socket_status, result.stdout)
                self.assertIn("NETWORK_BLOCKED", result.stdout)
                self.assertNotIn("host-only-secret", result.stdout)

    def test_memory_quota_kills_an_oversized_runtime_allocation(self) -> None:
        source = "payload = bytearray(512 * 1024 * 1024)\nprint('UNEXPECTED_ALLOCATION')\n"
        result = self.runner.run_batch(
            "python",
            source,
            [],
            "memory-probe",
            hashlib.sha256(source.encode("utf-8")).hexdigest(),
        )
        self.assertEqual((result.status, result.error_code, result.exit_code), ("runtime_error", "RUN_MEMORY", 137))
        self.assertNotIn("UNEXPECTED_ALLOCATION", result.stdout)


@settings(max_examples=8, deadline=None)
@given(
    left=st.integers(min_value=-25, max_value=25),
    operator=st.sampled_from(["+", "-", "*"]),
    right=st.integers(min_value=-25, max_value=25),
)
def test_generated_arithmetic_expressions_match_real_python_and_node(left: int, operator: str, right: int) -> None:
    operations = {"+": lambda: left + right, "-": lambda: left - right, "*": lambda: left * right}
    expected = str(operations[operator]()) + "\n"
    source = f"Inicio\nEscribir ({left} {operator} {right})\nFin\n"
    compiled = compile_source(source)
    assert compiled.translatable, [item.to_dict() for item in compiled.diagnostics]
    runner = OciRunner(timeout_seconds=5)
    for target in ("python", "javascript"):
        artifact = compiled.artifacts[target]
        result = runner.run_batch(target, artifact.source, [], compiled.source_hash, artifact.artifact_hash)
        assert (result.status, result.exit_code, result.stdout, result.stderr) == ("completed", 0, expected, "")


@settings(max_examples=5, deadline=None)
@given(
    value=st.text(
        alphabet=st.sampled_from(list('abYZ á漢✅"\\\n\t')),
        min_size=0,
        max_size=24,
    )
)
def test_generated_string_literals_round_trip_in_real_python_and_node(value: str) -> None:
    source = f"Inicio\nEscribir {json.dumps(value, ensure_ascii=False)}\nFin\n"
    compiled = compile_source(source)
    assert compiled.translatable, [item.to_dict() for item in compiled.diagnostics]
    runner = OciRunner(timeout_seconds=5)
    for target in ("python", "javascript"):
        artifact = compiled.artifacts[target]
        result = runner.run_batch(target, artifact.source, [], compiled.source_hash, artifact.artifact_hash)
        assert (result.status, result.exit_code, result.stdout, result.stderr) == (
            "completed",
            0,
            value + "\n",
            "",
        )


if __name__ == "__main__":
    unittest.main()
