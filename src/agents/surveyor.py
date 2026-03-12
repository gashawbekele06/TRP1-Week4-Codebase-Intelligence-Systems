from __future__ import annotations

import subprocess
from collections import Counter
from pathlib import Path
import ast

import networkx as nx

from src.analyzers.tree_sitter_analyzer import TreeSitterAnalyzer
from src.graph.knowledge_graph import KnowledgeGraph
from src.models.module import ModuleNode
from src.tracing import CartographyTracer


class SurveyorAgent:
    ANALYZABLE_SUFFIXES = {".py", ".sql", ".yml", ".yaml", ".js", ".jsx", ".ts", ".tsx"}

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.analyzer = TreeSitterAnalyzer(self.repo_root)
        self.graph = KnowledgeGraph()

    def run(
        self,
        days: int = 30,
        output_root: Path | None = None,
        changed_files: list[str] | None = None,
        tracer: CartographyTracer | None = None,
    ) -> dict:
        modules = self._analyze_modules(changed_files=changed_files)
        self._build_import_graph(modules)
        dead_code_candidates = self.identify_dead_code_candidates(modules)

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

        output_base = output_root.resolve() if output_root else self.repo_root
        output_path = output_base / ".cartography" / "module_graph.json"
        self.graph.write_json(output_path)

        if tracer is not None:
            tracer.log(
                agent="Surveyor",
                action="run",
                confidence=0.92,
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
            "module_count": len(modules),
            "edge_count": self.graph.module_graph.number_of_edges(),
            "pagerank": sorted(pagerank.items(), key=lambda item: item[1], reverse=True),
            "strongly_connected_components": strongly_connected,
            "git_velocity": dict(velocity),
            "high_velocity_core": high_velocity_core,
            "dead_code_candidates": dead_code_candidates,
            "module_graph_path": str(output_path),
            "analysis_scope": "incremental" if changed_files else "full",
            "analyzed_files": [m.path for m in modules],
        }

    def _analyze_modules(self, changed_files: list[str] | None = None) -> list[ModuleNode]:
        modules: list[ModuleNode] = []
        changed_set = {Path(item).as_posix() for item in (changed_files or [])}
        for path in sorted(self.repo_root.rglob("*")):
            if not path.is_file():
                continue
            if ".git" in path.parts or ".venv" in path.parts or path.parts.count(".cartography"):
                continue
            if path.suffix.lower() not in self.ANALYZABLE_SUFFIXES:
                continue

            rel_path = path.relative_to(self.repo_root).as_posix()
            if changed_set and rel_path not in changed_set:
                continue

            try:
                modules.append(self.analyzer.analyze_module(path))
            except Exception:
                # Graceful degradation on unparseable files.
                continue
        return modules

    def _build_import_graph(self, modules: list[ModuleNode]) -> None:
        for module in modules:
            self.graph.add_module_node(module.path, language=module.language)

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

    def identify_dead_code_candidates(self, modules: list[ModuleNode]) -> list[dict]:
        """Find exported symbols with no internal/external usage references."""
        symbol_defs: dict[str, tuple[str, int | None]] = {}
        python_modules = [m for m in modules if m.language == "python" and m.path.endswith(".py")]

        for module in python_modules:
            for fn in module.public_functions:
                symbol_defs[fn.name] = (module.path, fn.line_start)
            for cls in module.classes:
                symbol_defs[cls.name] = (module.path, cls.line_start)

        references: Counter[str] = Counter()
        for module in python_modules:
            file_path = self.repo_root / module.path
            try:
                tree = ast.parse(file_path.read_text(encoding="utf-8"))
            except Exception:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    references[node.id] += 1
                elif isinstance(node, ast.Attribute):
                    references[node.attr] += 1
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        references[alias.name] += 1

        dead: list[dict] = []
        for symbol, (module_path, line_start) in sorted(symbol_defs.items()):
            if references.get(symbol, 0) == 0:
                dead.append(
                    {
                        "symbol": symbol,
                        "module": module_path,
                        "line_start": line_start,
                        "reason": "no internal or external references found",
                    }
                )

        return dead
