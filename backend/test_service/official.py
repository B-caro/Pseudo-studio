from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OFFICIAL_CASES_PATH = ROOT / "examples/official-cases.json"


def official_data() -> dict[str, Any]:
    return json.loads(OFFICIAL_CASES_PATH.read_text(encoding="utf-8"))


def official_stdout(program: str, inputs: list[str], expected_tail: str) -> str:
    templates = official_data()["prompt_templates"][program]
    if program == "D":
        prompts = [templates[0], *(templates[1].format(index=index) for index in range(1, int(inputs[0]) + 1))]
    else:
        prompts = templates
    return "\n".join([*prompts, *expected_tail.split("\n")]) + "\n"


def official_case_requests(program: str) -> list[dict[str, Any]]:
    data = official_data()
    return [
        {
            "id": item["id"],
            "inputs": item["inputs"],
            "expected_stdout": official_stdout(program, item["inputs"], item["expected_tail"]),
        }
        for item in data["cases"]
        if item["program"] == program
    ]
