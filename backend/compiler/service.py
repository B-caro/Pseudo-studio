"""Public compiler pipeline used by API, CLI, tests, and the UI."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any

from backend.generators.codegen import GeneratedArtifact, GenerationError, generate

from .lexer import lex
from .model import Diagnostic, serialize
from .parser import parse
from .semantic import SemanticResult, analyze

COMPILER_VERSION = "0.1.0"


@dataclass(slots=True)
class CompileResult:
    compiler_version: str
    source_hash: str
    translatable: bool
    tokens: list[dict[str, Any]]
    ast: dict[str, Any] | None
    symbols: list[dict[str, Any]]
    diagnostics: list[Diagnostic]
    phases: dict[str, dict[str, Any]]
    artifacts: dict[str, GeneratedArtifact]

    def to_dict(self, *, include_code: bool = True) -> dict[str, Any]:
        return {
            "compiler_version": self.compiler_version,
            "source_hash": self.source_hash,
            "translatable": self.translatable,
            "tokens": self.tokens,
            "ast": self.ast,
            "symbols": self.symbols,
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "phases": self.phases,
            "artifacts": {
                target: artifact.to_dict()
                if include_code
                else {
                    "target": artifact.target,
                    "artifact_hash": artifact.artifact_hash,
                    "source_map": artifact.source_map,
                    "extension": artifact.extension,
                }
                for target, artifact in self.artifacts.items()
            },
        }


def compile_source(source: str, targets: tuple[str, ...] = ("python", "javascript")) -> CompileResult:
    source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
    diagnostics: list[Diagnostic] = []
    phases: dict[str, dict[str, Any]] = {}
    artifacts: dict[str, GeneratedArtifact] = {}

    started = time.perf_counter()
    lexical = lex(source)
    phases["lexical"] = {
        "status": "failed" if lexical.diagnostics else "ok",
        "duration_ms": (time.perf_counter() - started) * 1000,
    }
    diagnostics.extend(lexical.diagnostics)

    started = time.perf_counter()
    parsed = parse(lexical.tokens)
    phases["syntax"] = {
        "status": "failed" if parsed.diagnostics else "ok",
        "duration_ms": (time.perf_counter() - started) * 1000,
    }
    diagnostics.extend(parsed.diagnostics)

    semantic: SemanticResult | None = None
    if parsed.program is not None:
        started = time.perf_counter()
        semantic = analyze(parsed.program)
        phases["semantic"] = {
            "status": "failed" if semantic.diagnostics else "ok",
            "duration_ms": (time.perf_counter() - started) * 1000,
        }
        diagnostics.extend(semantic.diagnostics)
    else:
        phases["semantic"] = {"status": "skipped", "duration_ms": 0.0}

    translatable = parsed.program is not None and not any(item.severity == "error" for item in diagnostics)
    if translatable and semantic is not None:
        started = time.perf_counter()
        for target in targets:
            try:
                artifacts[target] = generate(parsed.program, semantic.symbols, target, validated=True)
            except GenerationError as error:
                diagnostics.append(Diagnostic("GEN_FAILED", "generation", "error", str(error), parsed.program.span))
                break
        phases["generation"] = {
            "status": "failed" if any(item.stage == "generation" for item in diagnostics) else "ok",
            "duration_ms": (time.perf_counter() - started) * 1000,
        }
    else:
        phases["generation"] = {"status": "blocked", "duration_ms": 0.0}
    translatable = translatable and not any(item.severity == "error" for item in diagnostics)
    if not translatable:
        artifacts.clear()

    return CompileResult(
        COMPILER_VERSION,
        source_hash,
        translatable,
        [token.to_dict() for token in lexical.tokens],
        serialize(parsed.program) if parsed.program is not None else None,
        [symbol.to_dict() for symbol in semantic.symbols] if semantic else [],
        diagnostics,
        phases,
        artifacts,
    )
