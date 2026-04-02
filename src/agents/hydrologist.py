from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import networkx as nx
from networkx.readwrite import json_graph

from src.analyzers.dag_config_parser import DAGConfigAnalyzer
from src.analyzers.python_dataflow import PythonDataFlowAnalyzer
from src.analyzers.sql_lineage import SQLLineageAnalyzer
from src.models.graph import DatasetNodeSchema, TransformationNodeSchema
from src.models.lineage import TransformationEvent
from src.tracing import CartographyTracer


class DataLineageGraph:
    """Typed lineage graph with explicit dataset and transformation nodes."""

    def __init__(self) -> None:
        self.graph = nx.DiGraph()

    def add_dataset(self, dataset_name: str) -> None:
        dataset = DatasetNodeSchema(
            name=dataset_name,
            storage_type="table",
        )
        dataset_data = dataset.model_dump(mode="json")
        self.graph.add_node(
            dataset_name,
            id=dataset_name,
            **dataset_data,
        )

    def add_transformation(self, event: TransformationEvent, ordinal: int) -> str:
        line_start = event.line_range[0] if event.line_range else 1
        trans_id = f"transformation::{event.source_file}:{line_start}:{ordinal}"
        trans = TransformationNodeSchema(
            source_datasets=list(event.source_datasets),
            target_datasets=list(event.target_datasets),
            transformation_type=event.transformation_type,
            source_file=event.source_file,
            line_range=event.line_range,
            sql_query_if_applicable=event.sql_query_if_applicable,
        )
        trans_data = trans.model_dump(mode="json")
        self.graph.add_node(
            trans_id,
            id=trans_id,
            **trans_data,
            notes=list(event.notes),
        )
        return trans_id

    def add_flow(self, src: str, trans_id: str, dst: str, event: TransformationEvent) -> None:
        self.graph.add_edge(
            src,
            trans_id,
            edge_type="CONSUMES",
            source_file=event.source_file,
            line_range=event.line_range,
        )
        self.graph.add_edge(
            trans_id,
            dst,
            edge_type="PRODUCES",
            source_file=event.source_file,
            line_range=event.line_range,
            sql_query_if_applicable=event.sql_query_if_applicable,
            notes=list(event.notes),
        )

    def dataset_nodes(self) -> list[str]:
        return sorted(
            node
            for node, attrs in self.graph.nodes(data=True)
            if isinstance(attrs, dict) and attrs.get("node_type") == "dataset"
        )

    def transformation_nodes(self) -> list[str]:
        return sorted(
            node
            for node, attrs in self.graph.nodes(data=True)
            if isinstance(attrs, dict) and attrs.get("node_type") == "transformation"
        )


class HydrologistAgent:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.python_analyzer = PythonDataFlowAnalyzer(self.repo_root)
        self.sql_analyzer = SQLLineageAnalyzer(self.repo_root)
        self.config_analyzer = DAGConfigAnalyzer(self.repo_root)
        self.data_lineage_graph = DataLineageGraph()
        self.lineage_graph = self.data_lineage_graph.graph
        self.warnings: list[str] = []

    def run(
        self,
        output_root: Path | None = None,
        changed_files: list[str] | None = None,
        tracer: CartographyTracer | None = None,
    ) -> dict:
        events = self._collect_events(changed_files=changed_files)
        self._build_lineage_graph(events)

        output_base = output_root.resolve() if output_root else self.repo_root
        output_path = output_base / ".cartography" / "lineage_graph.json"
        self._write_graph_json(output_path)

        if tracer is not None:
            tracer.log(
                agent="Hydrologist",
                action="run",
                confidence=0.91,
                analysis_method="static-analysis",
                evidence_sources=[
                    {"file": str(output_path), "line_range": "L1-L260", "method": "static-analysis"}
                ],
                metadata={
                    "changed_files_count": len(changed_files or []),
                    "analysis_scope": "incremental" if changed_files else "full",
                },
            )

        return {
            "event_count": len(events),
            "node_count": self.lineage_graph.number_of_nodes(),
            "edge_count": self.lineage_graph.number_of_edges(),
            "dataset_node_count": len(self.data_lineage_graph.dataset_nodes()),
            "transformation_node_count": len(self.data_lineage_graph.transformation_nodes()),
            "sources": self.find_sources(),
            "sinks": self.find_sinks(),
            "warnings": self.warnings,
            "lineage_graph_path": str(output_path),
            "analysis_scope": "incremental" if changed_files else "full",
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
        return sorted(
            item
            for item in visited
            if self.lineage_graph.nodes[item].get("node_type") == "dataset"
        )

    def find_sources(self) -> list[str]:
        return sorted(
            node
            for node in self.data_lineage_graph.dataset_nodes()
            if self.lineage_graph.in_degree(node) == 0
        )

    def find_sinks(self) -> list[str]:
        return sorted(
            node
            for node in self.data_lineage_graph.dataset_nodes()
            if self.lineage_graph.out_degree(node) == 0
        )

    def _collect_events(self, changed_files: list[str] | None = None) -> list[TransformationEvent]:
        events: list[TransformationEvent] = []
        changed_set = {Path(item).as_posix() for item in (changed_files or [])}
        for path in sorted(self.repo_root.rglob("*")):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or any(part.startswith(".") for part in path.parts):
                continue
            if ".git" in path.parts or ".venv" in path.parts or ".cartography" in path.parts:
                continue

            rel_path = path.relative_to(self.repo_root).as_posix()
            if changed_set and rel_path not in changed_set:
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
        for ordinal, event in enumerate(events, start=1):
            trans_id = self.data_lineage_graph.add_transformation(event, ordinal)

            sources = [
                src
                for src in event.source_datasets
                if src and src != "dynamic reference, cannot resolve"
            ]
            targets = [
                dst
                for dst in event.target_datasets
                if dst and dst != "dynamic reference, cannot resolve"
            ]

            for dataset in sources + targets:
                self.data_lineage_graph.add_dataset(dataset)

            if not sources or not targets:
                # Keep transformation node for auditability even when one side is dynamic.
                continue

            for src in sources:
                for dst in targets:
                    self.data_lineage_graph.add_flow(src, trans_id, dst, event)

    def _write_graph_json(self, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        links: list[dict[str, Any]] = []
        for source, target, attrs in self.lineage_graph.edges(data=True):
            edge_payload = dict(attrs)
            edge_payload["source"] = source
            edge_payload["target"] = target
            if edge_payload.get("edge_type") == "PRODUCES":
                if self.lineage_graph.nodes[source].get("node_type") == "transformation":
                    trans = self.lineage_graph.nodes[source]
                    edge_payload.setdefault("transformation_type", trans.get("transformation_type"))
                    edge_payload.setdefault("source_file", trans.get("source_file"))
                    edge_payload.setdefault("line_range", trans.get("line_range"))
                    edge_payload.setdefault(
                        "sql_query_if_applicable",
                        trans.get("sql_query_if_applicable"),
                    )
                    edge_payload.setdefault("notes", trans.get("notes", []))
            links.append(edge_payload)

        payload = {
            "graph": {
                **json_graph.node_link_data(self.lineage_graph),
                "links": links,
            },
            "sources": self.find_sources(),
            "sinks": self.find_sinks(),
            "dataset_nodes": self.data_lineage_graph.dataset_nodes(),
            "transformation_nodes": self.data_lineage_graph.transformation_nodes(),
            "warnings": self.warnings,
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
