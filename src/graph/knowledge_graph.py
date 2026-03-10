from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
from networkx.readwrite import json_graph


class KnowledgeGraph:
    def __init__(self) -> None:
        self.module_graph = nx.DiGraph()

    def add_module_node(self, module_path: str) -> None:
        self.module_graph.add_node(module_path)

    def add_import_edge(self, source_module: str, target_module: str) -> None:
        if self.module_graph.has_edge(source_module, target_module):
            self.module_graph[source_module][target_module]["weight"] += 1
        else:
            self.module_graph.add_edge(source_module, target_module, weight=1)

    def to_json_dict(self) -> dict:
        return json_graph.node_link_data(self.module_graph)

    def write_json(self, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(self.to_json_dict(), indent=2), encoding="utf-8")
