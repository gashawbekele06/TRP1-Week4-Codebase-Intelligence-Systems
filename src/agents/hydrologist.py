from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
from networkx.readwrite import json_graph

from src.analyzers.dag_config_parser import DAGConfigAnalyzer
from src.analyzers.python_dataflow import PythonDataFlowAnalyzer
from src.analyzers.sql_lineage import SQLLineageAnalyzer
from src.models.lineage import TransformationEvent


class HydrologistAgent:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.python_analyzer = PythonDataFlowAnalyzer(self.repo_root)
        self.sql_analyzer = SQLLineageAnalyzer(self.repo_root)
        self.config_analyzer = DAGConfigAnalyzer(self.repo_root)
        self.lineage_graph = nx.DiGraph()
        self.warnings: list[str] = []

    def run(self) -> dict:
        events = self._collect_events()
        self._build_lineage_graph(events)

        output_path = self.repo_root / ".cartography" / "lineage_graph.json"
        self._write_graph_json(output_path)

        return {
            "event_count": len(events),
            "node_count": self.lineage_graph.number_of_nodes(),
            "edge_count": self.lineage_graph.number_of_edges(),
            "sources": self.find_sources(),
            "sinks": self.find_sinks(),
            "warnings": self.warnings,
            "lineage_graph_path": str(output_path),
        }

    def blast_radius(self, node: str) -> list[str]:
        if node not in self.lineage_graph:
            return []
        visited: set[str] = set()
        stack = [node]
        while stack:
            current = stack.pop()
            for nxt in self.lineage_graph.successors(current):
                if nxt not in visited:
                    visited.add(nxt)
                    stack.append(nxt)
        return sorted(visited)

    def find_sources(self) -> list[str]:
        return sorted(node for node in self.lineage_graph.nodes if self.lineage_graph.in_degree(node) == 0)

    def find_sinks(self) -> list[str]:
        return sorted(node for node in self.lineage_graph.nodes if self.lineage_graph.out_degree(node) == 0)

    def _collect_events(self) -> list[TransformationEvent]:
        events: list[TransformationEvent] = []
        for path in sorted(self.repo_root.rglob("*")):
            if not path.is_file():
                continue
            if ".git" in path.parts or ".venv" in path.parts or ".cartography" in path.parts:
                continue

            if path.suffix.lower() == ".py":
                result = self.python_analyzer.analyze_file(path)
            elif path.suffix.lower() == ".sql":
                result = self.sql_analyzer.analyze_file(path)
            elif path.suffix.lower() in {".yml", ".yaml"}:
                result = self.config_analyzer.analyze_file(path)
            else:
                continue

            events.extend(result.events)
            self.warnings.extend(result.warnings)

        return events

    def _build_lineage_graph(self, events: list[TransformationEvent]) -> None:
        for event in events:
            for dataset in event.source_datasets + event.target_datasets:
                if dataset and dataset != "dynamic reference, cannot resolve":
                    self.lineage_graph.add_node(dataset)

            for src in event.source_datasets:
                for dst in event.target_datasets:
                    if (
                        not src
                        or not dst
                        or src == "dynamic reference, cannot resolve"
                        or dst == "dynamic reference, cannot resolve"
                    ):
                        continue
                    self.lineage_graph.add_edge(
                        src,
                        dst,
                        transformation_type=event.transformation_type,
                        source_file=event.source_file,
                        line_range=event.line_range,
                        sql_query_if_applicable=event.sql_query_if_applicable,
                        notes=event.notes,
                    )

    def _write_graph_json(self, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "graph": json_graph.node_link_data(self.lineage_graph),
            "sources": self.find_sources(),
            "sinks": self.find_sinks(),
            "warnings": self.warnings,
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
