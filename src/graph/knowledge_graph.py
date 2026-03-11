from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import networkx as nx
from networkx.readwrite import json_graph

from src.models.graph import (
    DatasetNodeSchema,
    EdgeSchema,
    FunctionNodeSchema,
    ModuleNodeSchema,
    TransformationNodeSchema,
)


NodeSchema = ModuleNodeSchema | DatasetNodeSchema | FunctionNodeSchema | TransformationNodeSchema


class KnowledgeGraph:
    def __init__(self) -> None:
        self.module_graph = nx.DiGraph()
        self.node_objects: dict[str, NodeSchema] = {}
        self.edge_objects: dict[tuple[str, str, str], EdgeSchema] = {}

    def add_module_node(self, module_path: str, language: str = "unknown") -> None:
        node = ModuleNodeSchema(path=module_path, language=language)
        self.add_node(module_path, node)

    def add_import_edge(self, source_module: str, target_module: str) -> None:
        key = (source_module, target_module, "IMPORTS")
        if key in self.edge_objects:
            existing = self.edge_objects[key]
            updated_weight = existing.weight + 1
            edge = existing.model_copy(update={"weight": updated_weight})
        else:
            edge = EdgeSchema(
                edge_type="IMPORTS",
                source=source_module,
                target=target_module,
                weight=1,
            )
        self.add_edge(edge)

    def add_node(self, node_id: str, node: NodeSchema | dict[str, Any]) -> None:
        node_obj = self._parse_node(node)
        self.node_objects[node_id] = node_obj
        self.module_graph.add_node(node_id, **node_obj.model_dump(mode="json"))

    def add_edge(self, edge: EdgeSchema | dict[str, Any]) -> None:
        edge_obj = EdgeSchema.model_validate(edge)
        key = (edge_obj.source, edge_obj.target, edge_obj.edge_type)
        self.edge_objects[key] = edge_obj
        self.module_graph.add_edge(
            edge_obj.source,
            edge_obj.target,
            **edge_obj.model_dump(mode="json", exclude={"source", "target"}),
        )

    def to_json_dict(self) -> dict:
        return json_graph.node_link_data(self.module_graph)

    @classmethod
    def load_from_json(cls, input_path: Path) -> KnowledgeGraph:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        graph_data = json_graph.node_link_graph(payload)

        instance = cls()
        instance.module_graph = nx.DiGraph(graph_data)

        for node_id, attrs in instance.module_graph.nodes(data=True):
            if isinstance(attrs, dict) and attrs.get("node_type"):
                node_obj = instance._parse_node(attrs)
            else:
                node_obj = ModuleNodeSchema(path=str(node_id), language="unknown")
            instance.node_objects[str(node_id)] = node_obj

        for source, target, attrs in instance.module_graph.edges(data=True):
            edge_data: dict[str, Any] = {
                "source": str(source),
                "target": str(target),
                "edge_type": attrs.get("edge_type", "IMPORTS") if isinstance(attrs, dict) else "IMPORTS",
                "weight": attrs.get("weight", 1) if isinstance(attrs, dict) else 1,
                "metadata": attrs.get("metadata", {}) if isinstance(attrs, dict) else {},
            }
            edge_obj = EdgeSchema.model_validate(edge_data)
            key = (edge_obj.source, edge_obj.target, edge_obj.edge_type)
            instance.edge_objects[key] = edge_obj

        return instance

    def write_json(self, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(self.to_json_dict(), indent=2), encoding="utf-8")

    def _parse_node(self, payload: NodeSchema | dict[str, Any]) -> NodeSchema:
        if isinstance(
            payload,
            (ModuleNodeSchema, DatasetNodeSchema, FunctionNodeSchema, TransformationNodeSchema),
        ):
            return payload

        node_type = payload.get("node_type")
        if node_type == "module":
            return ModuleNodeSchema.model_validate(payload)
        if node_type == "dataset":
            return DatasetNodeSchema.model_validate(payload)
        if node_type == "function":
            return FunctionNodeSchema.model_validate(payload)
        if node_type == "transformation":
            return TransformationNodeSchema.model_validate(payload)

        raise ValueError("Node payload must include a valid 'node_type'.")
