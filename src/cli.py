from __future__ import annotations

import argparse
from pathlib import Path

from src.orchestrator import AnalysisOrchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Brownfield Cartographer CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Run Phase 1+2+3 analysis")
    analyze.add_argument(
        "repo",
        nargs="?",
        default=".",
        help="Path to local repository or GitHub URL",
    )
    analyze.add_argument("--days", type=int, default=30, help="Git velocity lookback window")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "analyze":
        cwd = Path.cwd().resolve()
        result = AnalysisOrchestrator(cwd).run(target=args.repo, days=args.days)
        surveyor = result["surveyor"]
        hydro = result["hydrologist"]
        semantic = result["semanticist"]

        print("Phase 1 Surveyor completed")
        print(f"- Target analyzed: {result['target']}")
        print(f"- Resolved repo: {result['resolved_repo']}")
        print(f"- Modules analyzed: {surveyor['module_count']}")
        print(f"- Import edges: {surveyor['edge_count']}")
        print(f"- Graph JSON: {surveyor['module_graph_path']}")

        top_hubs = surveyor["pagerank"][:5]
        if top_hubs:
            print("- Top architectural hubs (PageRank):")
            for path, score in top_hubs:
                print(f"  - {path}: {score:.4f}")

        scc = surveyor["strongly_connected_components"]
        print(f"- Circular dependency groups: {len(scc)}")

        high_velocity = surveyor["high_velocity_core"]
        if high_velocity:
            print("- High-velocity core files:")
            for item in high_velocity:
                print(
                    f"  - {item['path']} (changes={item['change_count']}, "
                    f"cumulative_share={item['cumulative_share']})"
                )

        dead_code = surveyor["dead_code_candidates"]
        print(f"- Dead code candidates: {len(dead_code)}")
        for item in dead_code[:10]:
            print(f"  - {item['module']}:{item['line_start']} {item['symbol']}")

        print("\nPhase 2 Hydrologist completed")
        print(f"- Lineage events: {hydro['event_count']}")
        print(f"- Lineage nodes: {hydro['node_count']}")
        print(f"- Lineage edges: {hydro['edge_count']}")
        print(f"- Lineage JSON: {hydro['lineage_graph_path']}")
        print(f"- Sources discovered: {len(hydro['sources'])}")
        print(f"- Sinks discovered: {len(hydro['sinks'])}")

        print("\nPhase 3 Semanticist completed")
        print(f"- Modules semantically analyzed: {semantic['module_count']}")
        print(f"- Inferred business domains: {semantic['domain_count']}")
        print(f"- Semantic report JSON: {semantic['semantic_report_path']}")
        print(
            "- Model policy: "
            f"bulk={semantic['model_policy']['bulk_extraction_model']}, "
            f"synthesis={semantic['model_policy']['synthesis_model']}"
        )

        print("- Inferred domain boundaries:")
        for domain in semantic["domain_boundaries"]:
            print(f"  - {domain['domain']} ({domain['module_count']} modules)")

        warnings = semantic.get("warnings", [])
        if warnings:
            print("- Semanticist warnings:")
            for warning in warnings:
                print(f"  - {warning}")

        fde = semantic["five_fde_answers"]
        print("\nFive FDE Day-One Answers")
        print(f"1) {fde['q1_primary_ingestion_path']}")
        print(f"2) {fde['q2_critical_outputs']}")
        print(f"3) {fde['q3_blast_radius']}")
        print(f"4) {fde['q4_logic_concentration']}")
        print(f"5) {fde['q5_git_velocity_map']}")


if __name__ == "__main__":
    main()
