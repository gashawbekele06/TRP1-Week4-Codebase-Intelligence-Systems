from __future__ import annotations

import subprocess
from collections import Counter
from pathlib import Path

import networkx as nx

from src.analyzers.tree_sitter_analyzer import TreeSitterAnalyzer
from src.graph.knowledge_graph import KnowledgeGraph
from src.models.module import ModuleNode


class SurveyorAgent:
    ANALYZABLE_SUFFIXES = {".py", ".sql", ".yml", ".yaml", ".js", ".jsx", ".ts", ".tsx"}

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.analyzer = TreeSitterAnalyzer(self.repo_root)
        self.graph = KnowledgeGraph()

    def run(self, days: int = 30) -> dict:
        modules = self._analyze_modules()
        self._build_import_graph(modules)

        pagerank = (
            self._pagerank_python(self.graph.module_graph)
            if self.graph.module_graph.number_of_nodes()
            else {}
        )
        strongly_connected = [
            sorted(component)
            for component in nx.strongly_connected_components(self.graph.module_graph)
            if len(component) > 1
        ]

        velocity = self.extract_git_velocity(days=days)
        high_velocity_core = self.identify_high_velocity_core(velocity)

        output_path = self.repo_root / ".cartography" / "module_graph.json"
        self.graph.write_json(output_path)

        return {
            "module_count": len(modules),
            "edge_count": self.graph.module_graph.number_of_edges(),
            "pagerank": sorted(pagerank.items(), key=lambda item: item[1], reverse=True),
            "strongly_connected_components": strongly_connected,
            "git_velocity": dict(velocity),
            "high_velocity_core": high_velocity_core,
            "module_graph_path": str(output_path),
        }

    def _analyze_modules(self) -> list[ModuleNode]:
        modules: list[ModuleNode] = []
        for path in sorted(self.repo_root.rglob("*")):
            if not path.is_file():
                continue
            if ".git" in path.parts or ".venv" in path.parts or path.parts.count(".cartography"):
                continue
            if path.suffix.lower() not in self.ANALYZABLE_SUFFIXES:
                continue

            try:
                modules.append(self.analyzer.analyze_module(path))
            except Exception:
                # Graceful degradation on unparseable files.
                continue
        return modules

    def _build_import_graph(self, modules: list[ModuleNode]) -> None:
        for module in modules:
            self.graph.add_module_node(module.path)

        known_paths = {module.path for module in modules}
        dotted_to_path = {
            module.path.removesuffix(".py").replace("/", "."): module.path
            for module in modules
            if module.path.endswith(".py")
        }

        for module in modules:
            if module.language != "python":
                continue

            for imported in module.imports:
                target = dotted_to_path.get(imported)
                if target and target in known_paths:
                    self.graph.add_import_edge(module.path, target)

    def extract_git_velocity(self, days: int = 30) -> Counter[str]:
        """Count per-file git change frequency for the given rolling window."""
        cmd = [
            "git",
            "-C",
            str(self.repo_root),
            "log",
            f"--since={days}.days",
            "--name-only",
            "--pretty=format:",
            "--",
            ".",
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            return Counter()

        changes = Counter()
        for raw_line in result.stdout.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            changes[line] += 1
        return changes

    def identify_high_velocity_core(self, velocity: Counter[str]) -> list[dict]:
        """Return top ~20% of files that explain ~80% of observed file changes."""
        if not velocity:
            return []

        total_changes = sum(velocity.values())
        sorted_files = sorted(velocity.items(), key=lambda item: item[1], reverse=True)

        threshold = max(1, int(len(sorted_files) * 0.2))
        cumulative = 0
        high_velocity: list[dict] = []

        for index, (path, count) in enumerate(sorted_files):
            cumulative += count
            high_velocity.append(
                {
                    "path": path,
                    "change_count": count,
                    "cumulative_share": round(cumulative / total_changes, 4),
                }
            )
            if index + 1 >= threshold and cumulative / total_changes >= 0.8:
                break

        return high_velocity

    def _pagerank_python(
        self,
        graph: nx.DiGraph,
        alpha: float = 0.85,
        max_iter: int = 100,
        tol: float = 1.0e-6,
    ) -> dict[str, float]:
        """Pure-Python PageRank to avoid SciPy runtime dependency."""
        nodes = list(graph.nodes())
        n = len(nodes)
        if n == 0:
            return {}

        rank = {node: 1.0 / n for node in nodes}
        out_degree = {node: graph.out_degree(node) for node in nodes}

        for _ in range(max_iter):
            new_rank = {node: (1.0 - alpha) / n for node in nodes}
            dangling_sum = alpha * sum(rank[node] for node in nodes if out_degree[node] == 0) / n

            for node in nodes:
                new_rank[node] += dangling_sum

            for source in nodes:
                if out_degree[source] == 0:
                    continue
                share = alpha * rank[source] / out_degree[source]
                for target in graph.successors(source):
                    new_rank[target] += share

            delta = sum(abs(new_rank[node] - rank[node]) for node in nodes)
            rank = new_rank
            if delta < tol:
                break

        return rank
