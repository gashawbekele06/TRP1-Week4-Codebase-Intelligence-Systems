from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


NodeType = Literal["module", "dataset", "function", "transformation"]
EdgeType = Literal["IMPORTS", "PRODUCES", "CONSUMES", "CALLS", "CONFIGURES"]


class ModuleNodeSchema(BaseModel):
    node_type: Literal["module"] = "module"
    path: str
    language: str
    purpose_statement: str | None = None
    domain_cluster: str | None = None
    complexity_score: float | None = None
    change_velocity_30d: float | None = None
    is_dead_code_candidate: bool = False
    last_modified: datetime | None = None


class DatasetNodeSchema(BaseModel):
    node_type: Literal["dataset"] = "dataset"
    name: str
    storage_type: Literal["table", "file", "stream", "api"]
    schema_snapshot: dict | None = None
    freshness_sla: str | None = None
    owner: str | None = None
    is_source_of_truth: bool = False


class FunctionNodeSchema(BaseModel):
    node_type: Literal["function"] = "function"
    qualified_name: str
    parent_module: str
    signature: str | None = None
    purpose_statement: str | None = None
    call_count_within_repo: int = 0
    is_public_api: bool = True


class TransformationNodeSchema(BaseModel):
    node_type: Literal["transformation"] = "transformation"
    source_datasets: list[str] = Field(default_factory=list)
    target_datasets: list[str] = Field(default_factory=list)
    transformation_type: str
    source_file: str
    line_range: tuple[int, int] | None = None
    sql_query_if_applicable: str | None = None


class EdgeSchema(BaseModel):
    edge_type: EdgeType
    source: str
    target: str
    weight: int | float = 1
    metadata: dict = Field(default_factory=dict)


class GraphSchema(BaseModel):
    nodes: list[ModuleNodeSchema | DatasetNodeSchema | FunctionNodeSchema | TransformationNodeSchema] = (
        Field(default_factory=list)
    )
    edges: list[EdgeSchema] = Field(default_factory=list)
