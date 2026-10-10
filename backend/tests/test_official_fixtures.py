"""Integrity checks for the transcribed academic fixtures (not compiler tests)."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    "A-1": ("A", ["4", "2", "3"], "El resultado es: 16"),
    "A-2": ("A", ["10", "5", "2"], "El resultado es: 28"),
    "A-3": ("A", ["6", "3", "4"], "El resultado es: 34"),
    "B-1": ("B", ["8", "80"], "Aprobado"),
    "B-2": ("B", ["7", "60"], "Reprobado por asistencia"),
    "B-3": ("B", ["4", "90"], "Reprobado por nota"),
    "C-1": ("C", ["4"], "El factorial es: 24\nLa suma es: 20"),
    "C-2": ("C", ["5"], "El factorial es: 120\nLa suma es: 30"),
    "C-3": ("C", ["1"], "El factorial es: 1\nLa suma es: 2"),
    "D-1": ("D", ["3", "4", "9", "2"], "El promedio es: 5\nEl número mayor es: 9"),
    "D-2": ("D", ["4", "10", "20", "5", "15"], "El promedio es: 12.5\nEl número mayor es: 20"),
    "D-3": ("D", ["5", "1", "1", "1", "1", "1"], "El promedio es: 1\nEl número mayor es: 1"),
    "E-1": ("E", ["5", "4"], "El área es: 20\nClasificación: Pequeña"),
    "E-2": ("E", ["10", "8"], "El área es: 80\nClasificación: Grande"),
    "E-3": ("E", ["6", "9"], "El área es: 54\nClasificación: Grande"),
}


class OfficialFixtureTests(unittest.TestCase):
    def test_five_program_sources_exist_and_are_nonempty(self) -> None:
        manifest = json.loads((ROOT / "examples/official-cases.json").read_text())
        self.assertEqual(set(manifest["source_files"]), set("ABCDE"))
        for program, relative in manifest["source_files"].items():
            source = (ROOT / relative).read_text()
            self.assertTrue(source.strip(), program)
            self.assertTrue(source.startswith("Inicio\n"), program)
            self.assertTrue(source.rstrip().endswith("Fin"), program)

    def test_all_fifteen_official_datasets_and_results_are_recorded(self) -> None:
        manifest = json.loads((ROOT / "examples/official-cases.json").read_text())
        cases = {case["id"]: case for case in manifest["cases"]}
        self.assertEqual(set(cases), set(EXPECTED))
        for case_id, expected in EXPECTED.items():
            case = cases[case_id]
            self.assertEqual((case["program"], case["inputs"], case["expected_tail"]), expected)

    def test_academic_sources_preserve_required_constructs(self) -> None:
        sources = {name: (ROOT / f"examples/{name}.psc").read_text() for name in "ABCDE"}
        self.assertIn("((a + b) * c) - (a / b)", sources["A"])
        self.assertIn("(asistencia >= 75)", sources["B"])
        self.assertIn("suma = suma + (i * 2)", sources["C"])
        self.assertIn("Dimension numeros[n]", sources["D"])
        self.assertIn("numeros[i]", sources["D"])
        self.assertIn("Funcion area = CalcularArea(base, altura)", sources["E"])
        self.assertIn("Funcion clasificacion = ClasificarArea(area)", sources["E"])


if __name__ == "__main__":
    unittest.main()
