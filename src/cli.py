from __future__ import annotations

import argparse
from pathlib import Path

from src.agents.surveyor import SurveyorAgent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Brownfield Cartographer CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Run Phase 1 Surveyor analysis")
    analyze.add_argument("repo", nargs="?", default=".", help="Path to local repository")
    analyze.add_argument("--days", type=int, default=30, help="Git velocity lookback window")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "analyze":
        repo = Path(args.repo).resolve()
        result = SurveyorAgent(repo).run(days=args.days)

        print("Phase 1 Surveyor completed")
        print(f"- Modules analyzed: {result['module_count']}")
        print(f"- Import edges: {result['edge_count']}")
        print(f"- Graph JSON: {result['module_graph_path']}")

        top_hubs = result["pagerank"][:5]
        if top_hubs:
            print("- Top architectural hubs (PageRank):")
            for path, score in top_hubs:
                print(f"  - {path}: {score:.4f}")

        scc = result["strongly_connected_components"]
        print(f"- Circular dependency groups: {len(scc)}")

        high_velocity = result["high_velocity_core"]
        if high_velocity:
            print("- High-velocity core files:")
            for item in high_velocity:
                print(
                    f"  - {item['path']} (changes={item['change_count']}, "
                    f"cumulative_share={item['cumulative_share']})"
                )


if __name__ == "__main__":
    main()
