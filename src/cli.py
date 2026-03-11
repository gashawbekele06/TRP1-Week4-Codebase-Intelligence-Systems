from __future__ import annotations

import argparse
from pathlib import Path

from src.orchestrator import AnalysisOrchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Brownfield Cartographer CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Run Phase 1+2 analysis")
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


if __name__ == "__main__":
    main()
