from __future__ import annotations

from pydantic import BaseModel, Field


class FunctionInfo(BaseModel):
    name: str
    normalized_name: str
    line_start: int | None = None
    line_end: int | None = None


class ClassInfo(BaseModel):
    name: str
    bases: list[str] = Field(default_factory=list)
    line_start: int | None = None
    line_end: int | None = None


class ModuleNode(BaseModel):
    path: str
    language: str
    imports: list[str] = Field(default_factory=list)
    public_functions: list[FunctionInfo] = Field(default_factory=list)
    classes: list[ClassInfo] = Field(default_factory=list)
