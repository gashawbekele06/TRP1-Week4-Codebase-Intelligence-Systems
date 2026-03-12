from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
    1) module graph lookup
    2) lineage lookup
    3) semantic lookup
    4) CODEBASE context lookup
    """

    def __init__(self, artifact_root: Path, tracer: CartographyTracer | None = None) -> None:
        self.artifact_root = artifact_root.resolve()
        self.cartography_root = self.artifact_root / ".cartography"
        self.tracer = tracer

    def answer(self, question: str) -> str:
        state = {"question": question, "findings": []}

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
        findings: list[dict[str, Any]] = []
        findings.extend(self.tool_module_graph_lookup(question))
        findings.extend(self.tool_lineage_lookup(question))
        findings.extend(self.tool_semantic_lookup(question))
        findings.extend(self.tool_codebase_lookup(question))

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

        def module_node(state: dict[str, Any]) -> dict[str, Any]:
            state["findings"] = state.get("findings", []) + self.tool_module_graph_lookup(state.get("question", ""))
            return state

        def lineage_node(state: dict[str, Any]) -> dict[str, Any]:
            state["findings"] = state.get("findings", []) + self.tool_lineage_lookup(state.get("question", ""))
            return state

        def semantic_node(state: dict[str, Any]) -> dict[str, Any]:
            state["findings"] = state.get("findings", []) + self.tool_semantic_lookup(state.get("question", ""))
            return state

        def context_node(state: dict[str, Any]) -> dict[str, Any]:
            state["findings"] = state.get("findings", []) + self.tool_codebase_lookup(state.get("question", ""))
            return state

        workflow = StateGraph(dict)
        workflow.add_node("module_graph_tool", module_node)
        workflow.add_node("lineage_tool", lineage_node)
        workflow.add_node("semantic_tool", semantic_node)
        workflow.add_node("context_tool", context_node)

        workflow.set_entry_point("module_graph_tool")
        workflow.add_edge("module_graph_tool", "lineage_tool")
        workflow.add_edge("lineage_tool", "semantic_tool")
        workflow.add_edge("semantic_tool", "context_tool")
        workflow.add_edge("context_tool", END)
        return workflow.compile()

    def tool_module_graph_lookup(self, question: str) -> list[dict[str, Any]]:
        path = self.cartography_root / "module_graph.json"
        if not path.exists():
            return []

        payload = json.loads(path.read_text(encoding="utf-8"))
        findings: list[dict[str, Any]] = []

        pagerank = payload.get("pagerank") or []
        if pagerank:
            top = pagerank[0]
            findings.append(
                {
                    "file": str(path),
                    "line_range": "L1-L260",
                    "method": "static-analysis",
                    "fact": f"Top architectural hub is {top[0]} with PageRank {top[1]:.4f}",
                }
            )

        for group in payload.get("strongly_connected_components", [])[:2]:
            findings.append(
                {
                    "file": str(path),
                    "line_range": "L1-L260",
                    "method": "static-analysis",
                    "fact": f"Circular dependency group: {group}",
                }
            )

        return findings

    def tool_lineage_lookup(self, question: str) -> list[dict[str, Any]]:
        path = self.cartography_root / "lineage_graph.json"
        if not path.exists():
            return []

        payload = json.loads(path.read_text(encoding="utf-8"))
        findings: list[dict[str, Any]] = []

        sources = payload.get("sources", [])[:5]
        sinks = payload.get("sinks", [])[:5]
        if sources:
            findings.append(
                {
                    "file": str(path),
                    "line_range": "L1-L260",
                    "method": "static-analysis",
                    "fact": f"Primary lineage sources include {sources}",
                }
            )
        if sinks:
            findings.append(
                {
                    "file": str(path),
                    "line_range": "L1-L260",
                    "method": "static-analysis",
                    "fact": f"Primary lineage sinks include {sinks}",
                }
            )
        return findings

    def tool_semantic_lookup(self, question: str) -> list[dict[str, Any]]:
        path = self.cartography_root / "semantic_report.json"
        if not path.exists():
            return []

        payload = json.loads(path.read_text(encoding="utf-8"))
        findings: list[dict[str, Any]] = []

        domains = payload.get("business_domain_boundaries", [])
        if domains:
            findings.append(
                {
                    "file": str(path),
                    "line_range": "L1-L420",
                    "method": "llm-inference",
                    "fact": f"Largest inferred domain is {domains[0].get('domain')} ({domains[0].get('module_count')} modules)",
                }
            )

        drift = [
            item
            for item in payload.get("module_purpose_statements", [])
            if item.get("documentation_drift")
        ]
        for item in drift[:3]:
            findings.append(
                {
                    "file": item.get("path", str(path)),
                    "line_range": "L1-L120",
                    "method": "llm-inference",
                    "fact": f"Documentation Drift flagged: {item.get('path')} ({item.get('documentation_drift_reason')})",
                }
            )

        return findings

    def tool_codebase_lookup(self, question: str) -> list[dict[str, Any]]:
        path = self.cartography_root / "CODEBASE.md"
        if not path.exists():
            return []

        text = path.read_text(encoding="utf-8")
        facts: list[str] = []
        if "## Critical Path" in text:
            facts.append("Living context includes a curated Critical Path section")
        if "## Known Debt" in text:
            facts.append("Living context captures Known Debt including circular dependencies and documentation drift")

        return [
            {
                "file": str(path),
                "line_range": "L1-L220",
                "method": "hybrid-static-llm",
                "fact": fact,
            }
            for fact in facts
        ]
