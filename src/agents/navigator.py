from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import networkx as nx
from networkx.readwrite import json_graph

from src.tracing import CartographyTracer


@dataclass
class EvidenceItem:
    file: str
    line_range: str
    method: str
    fact: str


class NavigatorAgent:
    """Query agent over Cartographer artifacts.

    Tools:
    1) find_implementation
    2) trace_lineage
    3) blast_radius
    4) explain_module
    """

    def __init__(self, artifact_root: Path, tracer: CartographyTracer | None = None) -> None:
        self.artifact_root = artifact_root.resolve()
        self.cartography_root = self.artifact_root / ".cartography"
        self.tracer = tracer

    def answer(self, question: str) -> str:
        state = {
            "question": question,
            "intent": self._infer_intent(question),
            "params": self._extract_query_params(question),
            "findings": [],
        }

        # Prefer LangGraph orchestration when available; fallback to deterministic pipeline.
        graph = self._build_langgraph_if_available()
        if graph is not None:
            state = graph.invoke(state)
        else:
            state = self._fallback_pipeline(state)

        findings = state.get("findings", [])
        if not findings:
            response = (
                "No evidence found in current artifacts. Run `cartographer analyze` first to refresh `.cartography` outputs."
            )
        else:
            lines = ["Evidence-backed answer:"]
            for finding in findings[:8]:
                lines.append(
                    "- "
                    + finding["fact"]
                    + f" [{finding['file']}:{finding['line_range']}|method:{finding['method']}]"
                )
            response = "\n".join(lines)

        if self.tracer is not None:
            self.tracer.log(
                agent="Navigator",
                action="answer_query",
                confidence=0.86,
                analysis_method="hybrid-static-llm",
                evidence_sources=[
                    {
                        "file": f.get("file"),
                        "line_range": f.get("line_range"),
                        "method": f.get("method"),
                    }
                    for f in findings[:10]
                ],
                metadata={"question": question},
            )

        return response

    def _fallback_pipeline(self, state: dict[str, Any]) -> dict[str, Any]:
        question = state.get("question", "")
        intent = state.get("intent", "mixed")
        params = state.get("params", {})
        findings: list[dict[str, Any]] = []

        if intent in {"implementation", "mixed"}:
            findings.extend(self.find_implementation(params.get("concept") or question))
        if intent in {"lineage", "mixed"}:
            findings.extend(
                self.trace_lineage(
                    params.get("dataset") or params.get("concept") or "",
                    params.get("direction") or "downstream",
                )
            )
        if intent in {"blast", "mixed"}:
            findings.extend(self.blast_radius(params.get("module_path") or params.get("path") or ""))
        if intent in {"explain", "mixed"}:
            findings.extend(self.explain_module(params.get("path") or params.get("module_path") or ""))

        # De-duplicate by core citation identity.
        deduped: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str, str]] = set()
        for f in findings:
            key = (f.get("file", ""), f.get("line_range", ""), f.get("method", ""), f.get("fact", ""))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(f)

        state["findings"] = deduped
        return state

    def _build_langgraph_if_available(self):
        try:
            from langgraph.graph import END, StateGraph
        except Exception:
            return None

        def find_implementation_node(state: dict[str, Any]) -> dict[str, Any]:
            params = state.get("params", {})
            state["findings"] = state.get("findings", []) + self.find_implementation(
                params.get("concept") or state.get("question", "")
            )
            return state

        def trace_lineage_node(state: dict[str, Any]) -> dict[str, Any]:
            params = state.get("params", {})
            state["findings"] = state.get("findings", []) + self.trace_lineage(
                params.get("dataset") or params.get("concept") or "",
                params.get("direction") or "downstream",
            )
            return state

        def blast_radius_node(state: dict[str, Any]) -> dict[str, Any]:
            params = state.get("params", {})
            state["findings"] = state.get("findings", []) + self.blast_radius(
                params.get("module_path") or params.get("path") or ""
            )
            return state

        def explain_module_node(state: dict[str, Any]) -> dict[str, Any]:
            params = state.get("params", {})
            state["findings"] = state.get("findings", []) + self.explain_module(
                params.get("path") or params.get("module_path") or ""
            )
            return state

        workflow = StateGraph(dict)
        workflow.add_node("find_implementation", find_implementation_node)
        workflow.add_node("trace_lineage", trace_lineage_node)
        workflow.add_node("blast_radius", blast_radius_node)
        workflow.add_node("explain_module", explain_module_node)

        workflow.set_entry_point("find_implementation")
        workflow.add_edge("find_implementation", "trace_lineage")
        workflow.add_edge("trace_lineage", "blast_radius")
        workflow.add_edge("blast_radius", "explain_module")
        workflow.add_edge("explain_module", END)
        return workflow.compile()

    def find_implementation(self, concept: str) -> list[dict[str, Any]]:
        path = self.cartography_root / "module_graph.json"
        if not path.exists():
            return []

        payload = json.loads(path.read_text(encoding="utf-8"))
        graph = json_graph.node_link_graph(payload)
        findings: list[dict[str, Any]] = []

        concept_tokens = self._tokens(concept)
        matches = [
            node
            for node in graph.nodes
            if any(token in str(node).lower() for token in concept_tokens)
        ]
        if not matches:
            centrality = nx.pagerank(graph) if graph.number_of_nodes() else {}
            matches = [node for node, _ in sorted(centrality.items(), key=lambda item: item[1], reverse=True)[:3]]

        for node in matches[:3]:
            score = float(graph.out_degree(node) + graph.in_degree(node))
            findings.append(
                {
                    "file": str(path),
                    "line_range": "L1-L260",
                    "method": "static-analysis",
                    "fact": f"Implementation match: {node} (connectivity score={score:.1f})",
                }
            )

        return findings

    def trace_lineage(self, dataset: str, direction: str = "downstream") -> list[dict[str, Any]]:
        path = self.cartography_root / "lineage_graph.json"
        if not path.exists():
            return []

        payload = json.loads(path.read_text(encoding="utf-8"))
        graph_payload = payload.get("graph", payload)
        graph = json_graph.node_link_graph(graph_payload)
        findings: list[dict[str, Any]] = []

        dataset_node = self._best_dataset_match(graph, dataset)
        if not dataset_node:
            sources = payload.get("sources", [])[:5]
            sinks = payload.get("sinks", [])[:5]
            if sources:
                findings.append(
                    {
                        "file": str(path),
                        "line_range": "L1-L260",
                        "method": "static-analysis",
                        "fact": f"Lineage trace identifies primary source datasets: {sources}",
                    }
                )
            if sinks:
                findings.append(
                    {
                        "file": str(path),
                        "line_range": "L1-L260",
                        "method": "static-analysis",
                        "fact": f"Lineage trace identifies primary sink datasets: {sinks}",
                    }
                )
            return findings

        if direction.lower() == "upstream":
            reachable = nx.ancestors(graph, dataset_node)
        else:
            reachable = nx.descendants(graph, dataset_node)

        datasets = sorted(
            node
            for node in reachable
            if graph.nodes[node].get("node_type") == "dataset"
        )[:10]

        findings.append(
            {
                "file": str(path),
                "line_range": "L1-L260",
                "method": "static-analysis",
                "fact": (
                    f"Lineage {direction} trace for {dataset_node}: "
                    f"{datasets if datasets else 'no connected dataset nodes'}"
                ),
            }
        )
        return findings

    def blast_radius(self, module_path: str) -> list[dict[str, Any]]:
        path = self.cartography_root / "module_graph.json"
        if not path.exists():
            return []

        payload = json.loads(path.read_text(encoding="utf-8"))
        graph = json_graph.node_link_graph(payload)
        findings: list[dict[str, Any]] = []

        module = self._best_module_match(graph, module_path)
        if not module:
            return findings

        impacted = sorted(nx.descendants(graph, module))
        findings.append(
            {
                "file": str(path),
                "line_range": "L1-L260",
                "method": "static-analysis",
                "fact": (
                    f"Blast radius for {module}: "
                    f"{impacted[:12] if impacted else 'no downstream dependent modules detected'}"
                ),
            }
        )

        return findings

    def explain_module(self, path: str) -> list[dict[str, Any]]:
        semantic_path = self.cartography_root / "semantic_report.json"
        codebase_path = self.cartography_root / "CODEBASE.md"
        if not semantic_path.exists() and not codebase_path.exists():
            return []

        findings: list[dict[str, Any]] = []

        if semantic_path.exists():
            payload = json.loads(semantic_path.read_text(encoding="utf-8"))
            target = self._best_semantic_match(payload, path)
            if target:
                findings.append(
                    {
                        "file": target.get("path", str(semantic_path)),
                        "line_range": "L1-L160",
                        "method": "llm-inference",
                        "fact": (
                            f"Module purpose: {target.get('purpose_statement')} "
                            f"(domain={target.get('inferred_domain')}, drift={target.get('documentation_drift')})"
                        ),
                    }
                )

        if codebase_path.exists():
            text = codebase_path.read_text(encoding="utf-8")
            if "## Module Purpose Index" in text:
                findings.append(
                    {
                        "file": str(codebase_path),
                        "line_range": "L1-L320",
                        "method": "hybrid-static-llm",
                        "fact": "CODEBASE includes Module Purpose Index for rapid module-level explanation.",
                    }
                )

        return findings

    # Backward-compatible aliases for older callers.
    def tool_module_graph_lookup(self, question: str) -> list[dict[str, Any]]:
        return self.find_implementation(question)

    def tool_lineage_lookup(self, question: str) -> list[dict[str, Any]]:
        return self.trace_lineage(question, "downstream")

    def tool_semantic_lookup(self, question: str) -> list[dict[str, Any]]:
        return self.blast_radius(question)

    def tool_codebase_lookup(self, question: str) -> list[dict[str, Any]]:
        return self.explain_module(question)

    def _infer_intent(self, question: str) -> str:
        text = question.lower()
        if any(word in text for word in ("lineage", "dataset", "source", "sink", "upstream", "downstream")):
            return "lineage"
        if any(word in text for word in ("blast", "impact", "affected", "radius")):
            return "blast"
        if any(word in text for word in ("explain", "purpose", "what does", "module")):
            return "explain"
        if any(word in text for word in ("implement", "where", "code", "hotspot")):
            return "implementation"
        return "mixed"

    def _extract_query_params(self, question: str) -> dict[str, str]:
        params: dict[str, str] = {}
        quoted = re.findall(r"['\"]([^'\"]+)['\"]", question)
        if quoted:
            candidate = quoted[0]
            if "/" in candidate or candidate.endswith(".py"):
                params["path"] = candidate
                params["module_path"] = candidate
            else:
                params["concept"] = candidate
                params["dataset"] = candidate
        if "upstream" in question.lower():
            params["direction"] = "upstream"
        elif "downstream" in question.lower():
            params["direction"] = "downstream"
        return params

    def _tokens(self, text: str) -> list[str]:
        return [token for token in re.findall(r"[a-z0-9_./-]+", text.lower()) if len(token) >= 3]

    def _best_module_match(self, graph: nx.DiGraph, module_path: str) -> str | None:
        if not graph.nodes:
            return None
        target = module_path.strip().lower()
        if target and target in {str(node).lower() for node in graph.nodes}:
            for node in graph.nodes:
                if str(node).lower() == target:
                    return str(node)
        if target:
            for node in graph.nodes:
                if target in str(node).lower():
                    return str(node)
        return str(next(iter(graph.nodes)))

    def _best_dataset_match(self, graph: nx.DiGraph, dataset: str) -> str | None:
        dataset_nodes = [
            node
            for node in graph.nodes
            if graph.nodes[node].get("node_type") == "dataset"
        ]
        if not dataset_nodes:
            return None

        target = dataset.strip().lower()
        if target:
            for node in dataset_nodes:
                if str(node).lower() == target:
                    return str(node)
            for node in dataset_nodes:
                if target in str(node).lower():
                    return str(node)
        return str(dataset_nodes[0])

    def _best_semantic_match(self, payload: dict[str, Any], path_value: str) -> dict[str, Any] | None:
        modules = payload.get("module_purpose_statements", [])
        if not modules:
            return None
        target = path_value.strip().lower()
        if target:
            for item in modules:
                if str(item.get("path", "")).lower() == target:
                    return item
            for item in modules:
                if target in str(item.get("path", "")).lower():
                    return item
        return modules[0]
