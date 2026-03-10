from __future__ import annotations

from pathlib import Path

import yaml

from src.models.lineage import AnalyzerResult, TransformationEvent


class DAGConfigAnalyzer:
    """Parse YAML config topology from dbt schema files and generic DAG-like configs."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()

    def analyze_file(self, file_path: Path) -> AnalyzerResult:
        if file_path.suffix.lower() not in {".yml", ".yaml"}:
            return AnalyzerResult()

        relative = str(file_path.relative_to(self.repo_root))
        content = file_path.read_text(encoding="utf-8")
        try:
            data = yaml.safe_load(content)
        except Exception:
            return AnalyzerResult(warnings=[f"{relative}: yaml parse failed"])

        if not isinstance(data, dict):
            return AnalyzerResult()

        events: list[TransformationEvent] = []
        warnings: list[str] = []

        # dbt schema topology
        if "models" in data and isinstance(data["models"], list):
            for model in data["models"]:
                if not isinstance(model, dict):
                    continue
                model_name = model.get("name")
                depends = model.get("depends_on", [])
                if isinstance(depends, dict):
                    depends = depends.get("nodes", [])
                if not isinstance(depends, list):
                    depends = []

                if model_name:
                    events.append(
                        TransformationEvent(
                            source_datasets=[str(dep) for dep in depends],
                            target_datasets=[str(model_name)],
                            transformation_type="config:dbt_model_dependency",
                            source_file=relative,
                            line_range=(1, max(1, len(content.splitlines()))),
                        )
                    )

        # dbt sources as source-of-truth nodes
        if "sources" in data and isinstance(data["sources"], list):
            for src in data["sources"]:
                if not isinstance(src, dict):
                    continue
                src_name = src.get("name")
                tables = src.get("tables", [])
                if not src_name or not isinstance(tables, list):
                    continue
                for table in tables:
                    if not isinstance(table, dict):
                        continue
                    table_name = table.get("name")
                    if not table_name:
                        continue
                    events.append(
                        TransformationEvent(
                            source_datasets=[],
                            target_datasets=[f"{src_name}.{table_name}"],
                            transformation_type="config:dbt_source",
                            source_file=relative,
                            line_range=(1, max(1, len(content.splitlines()))),
                        )
                    )

        # Generic YAML task topology
        tasks = data.get("tasks")
        if isinstance(tasks, list):
            task_names = {str(item.get("id")) for item in tasks if isinstance(item, dict) and item.get("id")}
            for task in tasks:
                if not isinstance(task, dict) or "id" not in task:
                    continue
                current = str(task["id"])
                upstream = task.get("upstream", [])
                if isinstance(upstream, str):
                    upstream = [upstream]
                if not isinstance(upstream, list):
                    upstream = []

                filtered = [str(item) for item in upstream if str(item) in task_names]
                events.append(
                    TransformationEvent(
                        source_datasets=filtered,
                        target_datasets=[current],
                        transformation_type="config:task_dependency",
                        source_file=relative,
                        line_range=(1, max(1, len(content.splitlines()))),
                    )
                )

        if not events and not warnings:
            warnings.append(f"{relative}: no recognizable DAG topology extracted")

        return AnalyzerResult(events=events, warnings=warnings)
