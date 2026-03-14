from __future__ import annotations

import re
from pathlib import Path

import sqlglot
from sqlglot import expressions as exp

from src.models.lineage import AnalyzerResult, TransformationEvent


class SQLLineageAnalyzer:
    DIALECTS = ["postgres", "bigquery", "snowflake", "duckdb"]

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()

    def analyze_file(self, file_path: Path) -> AnalyzerResult:
        if file_path.suffix.lower() != ".sql":
            return AnalyzerResult()

        raw_sql = file_path.read_text(encoding="utf-8")
        normalized_sql = self._normalize_dbt_refs(raw_sql)
        relative = str(file_path.relative_to(self.repo_root))
        target_dataset = self._infer_target_dataset(file_path)
        dbt_dependencies = self._extract_dbt_dependencies(raw_sql)

        warnings: list[str] = []
        tables: set[str] = set()
        parsed_success = False

        for dialect in self.DIALECTS:
            try:
                statements = sqlglot.parse(normalized_sql, read=dialect)
            except Exception:
                continue

            parsed_success = True
            for statement in statements:
                cte_names = {
                    cte.alias_or_name
                    for cte in statement.find_all(exp.CTE)
                    if cte.alias_or_name
                }
                for table in statement.find_all(exp.Table):
                    name = table.sql(dialect=dialect)
                    if name and name not in cte_names:
                        tables.add(name)
            if tables:
                break

        if not parsed_success:
            warnings.append(f"{relative}: sqlglot parse failed across dialects")

        source_datasets = sorted((tables | dbt_dependencies) - {target_dataset})

        if not tables and dbt_dependencies:
            warnings.append(f"{relative}: used dbt ref/source fallback extraction for lineage dependencies")

        event = TransformationEvent(
            source_datasets=source_datasets,
            target_datasets=[target_dataset],
            transformation_type="sql:model_build",
            source_file=relative,
            line_range=(1, max(1, len(raw_sql.splitlines()))),
            sql_query_if_applicable=raw_sql,
            notes=[],
        )

        return AnalyzerResult(events=[event], warnings=warnings)

    def _normalize_dbt_refs(self, sql: str) -> str:
        sql = re.sub(
            r"\{\{\s*ref\(['\"]([^'\"]+)['\"]\)\s*\}\}",
            lambda m: m.group(1),
            sql,
            flags=re.IGNORECASE,
        )
        sql = re.sub(
            r"\{\{\s*source\(['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\)\s*\}\}",
            lambda m: f"{m.group(1)}.{m.group(2)}",
            sql,
            flags=re.IGNORECASE,
        )
        return sql

    def _infer_target_dataset(self, file_path: Path) -> str:
        try:
            relative = file_path.relative_to(self.repo_root)
        except ValueError:
            relative = file_path

        if "models" in relative.parts:
            return file_path.stem
        return str(relative.with_suffix(""))

    def _extract_dbt_dependencies(self, raw_sql: str) -> set[str]:
        dependencies: set[str] = set()

        for match in re.findall(
            r"\{\{\s*ref\(['\"]([^'\"]+)['\"]\)\s*\}\}",
            raw_sql,
            flags=re.IGNORECASE,
        ):
            name = match.strip()
            if name:
                dependencies.add(name)

        for source_name, table_name in re.findall(
            r"\{\{\s*source\(['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\)\s*\}\}",
            raw_sql,
            flags=re.IGNORECASE,
        ):
            source_name = source_name.strip()
            table_name = table_name.strip()
            if source_name and table_name:
                dependencies.add(f"{source_name}.{table_name}")
            elif table_name:
                dependencies.add(table_name)

        return dependencies
