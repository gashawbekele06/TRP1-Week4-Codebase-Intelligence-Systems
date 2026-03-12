from __future__ import annotations

from pathlib import Path

from src.tracing import CartographyTracer


class ArchivistAgent:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()

    def generate_CODEBASE_md(
        self,
        *,
        surveyor_result: dict,
        hydrologist_result: dict,
        semanticist_result: dict,
        output_root: Path | None = None,
        tracer: CartographyTracer | None = None,
    ) -> dict:
        output_base = output_root.resolve() if output_root else self.repo_root
        output_path = output_base / ".cartography" / "CODEBASE.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        top_hubs = surveyor_result.get("pagerank", [])[:5]
        sources = hydrologist_result.get("sources", [])
        sinks = hydrologist_result.get("sinks", [])
        scc = surveyor_result.get("strongly_connected_components", [])
        high_velocity = surveyor_result.get("high_velocity_core", [])

        semantic_report_path = semanticist_result.get("semantic_report_path")
        drift_entries = self._extract_documentation_drift_entries(semantic_report_path)

        architecture_overview = self._build_architecture_overview(
            surveyor_result=surveyor_result,
            hydrologist_result=hydrologist_result,
            semanticist_result=semanticist_result,
        )

        lines: list[str] = []
        lines.append("# CODEBASE: Living Context")
        lines.append("")
        lines.append("## Architecture Overview")
        lines.append(architecture_overview)
        lines.append("")

        lines.append("## Critical Path (Top 5 by PageRank)")
        if top_hubs:
            for idx, item in enumerate(top_hubs, start=1):
                path, score = item
                lines.append(f"{idx}. `{path}` — PageRank `{score:.4f}` [static-analysis]")
        else:
            lines.append("- No PageRank hubs available.")
        lines.append("")

        lines.append("## Data Sources & Sinks")
        lines.append("### Sources")
        if sources:
            for src in sources[:20]:
                lines.append(f"- `{src}` [static-analysis]")
        else:
            lines.append("- No lineage sources discovered.")
        lines.append("")
        lines.append("### Sinks")
        if sinks:
            for sink in sinks[:20]:
                lines.append(f"- `{sink}` [static-analysis]")
        else:
            lines.append("- No lineage sinks discovered.")
        lines.append("")

        lines.append("## Known Debt")
        lines.append("### Circular Dependencies")
        if scc:
            for idx, group in enumerate(scc, start=1):
                lines.append(f"- Group {idx}: {', '.join(f'`{item}`' for item in group)} [static-analysis]")
        else:
            lines.append("- No circular dependency groups discovered.")
        lines.append("")
        lines.append("### Documentation Drift Flags")
        if drift_entries:
            for drift in drift_entries:
                lines.append(
                    f"- `{drift['path']}` {drift['line_range']} — {drift['reason']} [llm-inference]"
                )
        else:
            lines.append("- No documentation drift flags discovered.")
        lines.append("")

        lines.append("## High-Velocity Files")
        if high_velocity:
            for item in high_velocity:
                lines.append(
                    "- `"
                    + f"{item['path']}` — changes={item['change_count']}, cumulative_share={item['cumulative_share']} "
                    + "[static-analysis]"
                )
        else:
            lines.append("- No high-velocity files in selected lookback window.")
        lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")

        if tracer is not None:
            tracer.log(
                agent="Archivist",
                action="generate_CODEBASE_md",
                confidence=0.93,
                analysis_method="hybrid-static-llm",
                evidence_sources=[
                    {"file": surveyor_result.get("module_graph_path"), "line_range": "L1-L200", "method": "static-analysis"},
                    {"file": hydrologist_result.get("lineage_graph_path"), "line_range": "L1-L200", "method": "static-analysis"},
                    {"file": semantic_report_path, "line_range": "L1-L300", "method": "llm-inference"},
                ],
                metadata={"output_path": str(output_path)},
            )

        return {"codebase_md_path": str(output_path)}

    def _build_architecture_overview(
        self,
        *,
        surveyor_result: dict,
        hydrologist_result: dict,
        semanticist_result: dict,
    ) -> str:
        module_count = surveyor_result.get("module_count", 0)
        edge_count = surveyor_result.get("edge_count", 0)
        lineage_nodes = hydrologist_result.get("node_count", 0)
        lineage_edges = hydrologist_result.get("edge_count", 0)
        domain_count = semanticist_result.get("domain_count", 0)
        return (
            "This repository is organized as an analysis-focused architecture where static structure ("
            f"{module_count} modules, {edge_count} import edges) is combined with data lineage "
            f"({lineage_nodes} datasets, {lineage_edges} lineage edges) and semantic domain inference "
            f"({domain_count} inferred domains) to provide operational intelligence for maintenance, risk assessment, and onboarding."
        )

    def _extract_documentation_drift_entries(self, semantic_report_path: str | None) -> list[dict]:
        if not semantic_report_path:
            return []

        path = Path(semantic_report_path)
        if not path.exists():
            return []

        try:
            import json

            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

        entries = []
        for item in payload.get("module_purpose_statements", []):
            if item.get("documentation_drift"):
                entries.append(
                    {
                        "path": item.get("path", "unknown"),
                        "line_range": "[L1-L120]",
                        "reason": item.get("documentation_drift_reason")
                        or "Documentation Drift flagged by Semanticist.",
                    }
                )
        return entries[:50]
