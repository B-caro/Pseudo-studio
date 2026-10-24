from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Target = Literal["python", "javascript"]
ExportKind = Literal[
    "source",
    "python",
    "javascript",
    "python-txt",
    "javascript-txt",
    "tokens",
    "ast",
    "symbols",
    "diagnostics",
    "diagnostics-txt",
    "phases",
    "report-json",
    "report-markdown",
    "report-pdf",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SourceRequest(StrictModel):
    source: str = Field(min_length=1, max_length=1_000_000)

    @field_validator("source")
    @classmethod
    def source_size_in_bytes(cls, source: str) -> str:
        if len(source.encode("utf-8")) > 1_000_000:
            raise ValueError("La fuente supera el límite de 1 MB UTF-8.")
        return source


class TranslateRequest(SourceRequest):
    targets: list[Target] = Field(default_factory=lambda: ["python", "javascript"], min_length=1, max_length=2)


class RunInputs(StrictModel):
    values: list[str] = Field(default_factory=list, max_length=256)

    @field_validator("values")
    @classmethod
    def input_values_are_single_line(cls, values: list[str]) -> list[str]:
        if any("\n" in value or "\r" in value for value in values):
            raise ValueError("Cada entrada debe ocupar una sola línea.")
        if sum(len(value.encode("utf-8")) for value in values) > 65_536:
            raise ValueError("Las entradas combinadas superan 64 KiB.")
        return values


class RunRequest(SourceRequest):
    target: Target
    inputs: RunInputs = Field(default_factory=RunInputs)
    project_id: str | None = None
    run_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{1,64}$")


class TestCaseRequest(StrictModel):
    id: str = Field(min_length=1, max_length=80)
    inputs: list[str] = Field(default_factory=list, max_length=256)
    expected_stdout: str = Field(max_length=65_536)

    @field_validator("inputs")
    @classmethod
    def input_values_are_bounded_lines(cls, values: list[str]) -> list[str]:
        if any("\n" in value or "\r" in value for value in values):
            raise ValueError("Cada entrada debe ocupar una sola línea.")
        if sum(len(value.encode("utf-8")) for value in values) > 65_536:
            raise ValueError("Las entradas combinadas superan 64 KiB.")
        return values


class TestRunRequest(StrictModel):
    source: str | None = Field(default=None, max_length=1_000_000)
    example_id: Literal["A", "B", "C", "D", "E"] | None = None
    project_id: str | None = None
    test_cases: list[TestCaseRequest] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def require_source_or_example_and_cases(self) -> TestRunRequest:
        if (self.source is None) == (self.example_id is None):
            raise ValueError("Indique source o example_id, exactamente uno.")
        if self.source is not None and not self.test_cases:
            raise ValueError("Una fuente propia requiere al menos un caso de prueba.")
        if self.source is not None and len(self.source.encode("utf-8")) > 1_000_000:
            raise ValueError("La fuente supera el límite de 1 MB UTF-8.")
        return self


class ProjectCreateRequest(StrictModel):
    name: str = Field(min_length=1, max_length=120)
    source: str = Field(min_length=1, max_length=1_000_000)

    @field_validator("source")
    @classmethod
    def source_size_in_bytes(cls, source: str) -> str:
        if len(source.encode("utf-8")) > 1_000_000:
            raise ValueError("La fuente supera el límite de 1 MB UTF-8.")
        return source


class ProjectUpdateRequest(ProjectCreateRequest):
    version: int = Field(ge=1)


class ExportRequest(StrictModel):
    kind: ExportKind
    source: str | None = Field(default=None, max_length=1_000_000)
    report_id: str | None = None

    @model_validator(mode="after")
    def require_payload(self) -> ExportRequest:
        if self.kind.startswith("report-"):
            if self.report_id is None or self.source is not None:
                raise ValueError("La exportación de informe requiere report_id.")
        elif self.source is None or self.report_id is not None:
            raise ValueError("La exportación de artefacto requiere source.")
        if self.source is not None and len(self.source.encode("utf-8")) > 1_000_000:
            raise ValueError("La fuente supera el límite de 1 MB UTF-8.")
        return self
