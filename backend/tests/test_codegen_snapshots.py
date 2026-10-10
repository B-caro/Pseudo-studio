from pathlib import Path

from backend.compiler.service import compile_source

ROOT = Path(__file__).resolve().parents[2]


def test_real_generator_output_matches_checked_in_golden_files() -> None:
    snapshots = Path(__file__).parent / "snapshots"
    for program in "ABCDE":
        source = (ROOT / "examples" / f"{program}.psc").read_text(encoding="utf-8")
        result = compile_source(source)
        assert result.translatable, [diagnostic.to_dict() for diagnostic in result.diagnostics]
        for target, extension in (("python", ".py"), ("javascript", ".js")):
            actual = result.artifacts[target].source
            expected = (snapshots / f"{program}{extension}.snapshot").read_text(encoding="utf-8")
            assert actual == expected, f"Cambió el codegen de {program} para {target}"
