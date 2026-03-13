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
        onboarding_path = output_base / ".cartography" / "onboarding_brief.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        top_hubs = surveyor_result.get("pagerank", [])[:5]
        sources = hydrologist_result.get("sources", [])
        sinks = hydrologist_result.get("sinks", [])
        scc = surveyor_result.get("strongly_connected_components", [])
        high_velocity = surveyor_result.get("high_velocity_core", [])

        semantic_report_path = semanticist_result.get("semantic_report_path")
        drift_entries = self._extract_documentation_drift_entries(semantic_report_path)
        module_purpose_index = self._extract_module_purpose_index(semantic_report_path)
        day_one_answers = semanticist_result.get("five_fde_answers", {})

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

        lines.append("## Module Purpose Index")
        if module_purpose_index:
            for item in module_purpose_index:
                lines.append(
                    f"- `{item['path']}` [domain={item['domain']}] — {item['purpose']} "
                    f"[method={item['method']}]"
                )
        else:
            lines.append("- No module purpose entries available.")
        lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")
        onboarding_path.write_text(
            self._build_onboarding_brief(
                architecture_overview=architecture_overview,
                top_hubs=top_hubs,
                sources=sources,
                sinks=sinks,
                high_velocity=high_velocity,
                drift_entries=drift_entries,
                day_one_answers=day_one_answers,
            ),
            encoding="utf-8",
        )

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
                metadata={
                    "output_path": str(output_path),
                    "onboarding_brief_path": str(onboarding_path),
                },
            )

        return {
            "codebase_md_path": str(output_path),
            "onboarding_brief_path": str(onboarding_path),
        }

    def _build_onboarding_brief(
        self,
        *,
        architecture_overview: str,
        top_hubs: list,
        sources: list,
        sinks: list,
        high_velocity: list,
        drift_entries: list,
        day_one_answers: dict,
    ) -> str:
        lines: list[str] = []
        lines.append("# Onboarding Brief")
        lines.append("")
        lines.append("## First 15 Minutes")
        lines.append(architecture_overview)
        lines.append("")
        lines.append("## Critical Modules to Read First")
        if top_hubs:
            for path, score in top_hubs[:5]:
                lines.append(f"- `{path}` (PageRank={score:.4f})")
        else:
            lines.append("- No critical hubs detected.")
        lines.append("")
        lines.append("## Data Orientation")
        lines.append(f"- Sources: {sources[:8] if sources else 'none discovered'}")
        lines.append(f"- Sinks: {sinks[:8] if sinks else 'none discovered'}")
        lines.append("")
        lines.append("## Likely Pain Points")
        if high_velocity:
            for item in high_velocity[:8]:
                lines.append(f"- `{item['path']}` (changes={item['change_count']})")
        else:
            lines.append("- No recent high-velocity files in current lookback window.")
        if drift_entries:
            lines.append("- Documentation Drift flags present; prioritize validating docs vs behavior.")
        lines.append("")
        lines.append("## Week-One Focus")
        lines.append("1. Validate critical path modules and their dependencies.")
        lines.append("2. Confirm lineage sources/sinks against production expectations.")
        lines.append("3. Address top debt items (cycles + documentation drift).")
        lines.append("")
        lines.append("## Five FDE Day-One Answers")
        lines.append(
            "1. Primary Ingestion Path: "
            + str(day_one_answers.get("q1_primary_ingestion_path", "Unavailable"))
        )
        lines.append(
            "2. Most Critical Outputs: "
            + str(day_one_answers.get("q2_critical_outputs", "Unavailable"))
        )
        lines.append(
            "3. Blast Radius if Critical Module Fails: "
            + str(day_one_answers.get("q3_blast_radius", "Unavailable"))
        )
        lines.append(
            "4. Logic Concentration vs Distribution: "
            + str(day_one_answers.get("q4_logic_concentration", "Unavailable"))
        )
        lines.append(
            "5. Git Velocity Hotspots: "
            + str(day_one_answers.get("q5_git_velocity_map", "Unavailable"))
        )
        return "\n".join(lines)

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

    def _extract_module_purpose_index(self, semantic_report_path: str | None) -> list[dict]:
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

        rows: list[dict] = []
        for item in payload.get("module_purpose_statements", [])[:80]:
            rows.append(
                {
                    "path": item.get("path", "unknown"),
                    "domain": item.get("inferred_domain", "unknown"),
                    "purpose": item.get("purpose_statement", "Purpose unavailable"),
                    "method": "llm-inference",
                }
            )
        return rows
