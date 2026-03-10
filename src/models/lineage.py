from __future__ import annotations

from pydantic import BaseModel, Field


class TransformationEvent(BaseModel):
    source_datasets: list[str] = Field(default_factory=list)
    target_datasets: list[str] = Field(default_factory=list)
    transformation_type: str
    source_file: str
    line_range: tuple[int, int] | None = None
    sql_query_if_applicable: str | None = None
    notes: list[str] = Field(default_factory=list)


class AnalyzerResult(BaseModel):
    events: list[TransformationEvent] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
