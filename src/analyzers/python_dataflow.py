from __future__ import annotations

import ast
from pathlib import Path

import sqlglot
from sqlglot import expressions as exp

from src.analyzers.tree_sitter_analyzer import LanguageRouter
from src.models.lineage import AnalyzerResult, TransformationEvent


class PythonDataFlowAnalyzer:
    """Extract data-flow lineage signals from Python data engineering code."""

    DIALECTS = ["postgres", "bigquery", "snowflake", "duckdb"]

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.router = LanguageRouter()

    def analyze_file(self, file_path: Path) -> AnalyzerResult:
        if self.router.get_language_for_path(file_path) != "python":
            return AnalyzerResult()

        relative = str(file_path.relative_to(self.repo_root))
        events: list[TransformationEvent] = []
        warnings: list[str] = []

        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        string_bindings = self._collect_string_bindings(tree)

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            call_name = self._call_name(node.func)
            if not call_name:
                continue

            # pandas reads
            if call_name.endswith("read_csv"):
                dataset, note = self._extract_arg_value(
                    node,
                    0,
                    {"filepath_or_buffer"},
                    string_bindings,
                )
                event = self._build_read_event(
                    source_file=relative,
                    line=node.lineno,
                    source_dataset=dataset,
                    transformation_type="python:pandas_read_csv",
                    note=note,
                )
                events.append(event)

            elif call_name.endswith("read_sql"):
                sql_text, note = self._extract_arg_value(node, 0, {"sql"}, string_bindings)
                sources = self._extract_tables_from_sql(sql_text) if sql_text else []
                event = TransformationEvent(
                    source_datasets=sources or (["dynamic reference, cannot resolve"] if note else []),
                    target_datasets=[f"python_runtime:{relative}"],
                    transformation_type="python:pandas_read_sql",
                    source_file=relative,
                    line_range=(node.lineno, getattr(node, "end_lineno", node.lineno)),
                    sql_query_if_applicable=sql_text,
                    notes=[note] if note else [],
                )
                events.append(event)

            # SQLAlchemy execute
            elif call_name.endswith("execute"):
                sql_text, note = self._extract_arg_value(
                    node,
                    0,
                    {"statement", "clause"},
                    string_bindings,
                )
                sources = self._extract_tables_from_sql(sql_text) if sql_text else []
                event = TransformationEvent(
                    source_datasets=sources or (["dynamic reference, cannot resolve"] if note else []),
                    target_datasets=[f"python_runtime:{relative}"],
                    transformation_type="python:sqlalchemy_execute",
                    source_file=relative,
                    line_range=(node.lineno, getattr(node, "end_lineno", node.lineno)),
                    sql_query_if_applicable=sql_text,
                    notes=[note] if note else [],
                )
                events.append(event)

            # PySpark reads
            elif ".read." in call_name and any(
                call_name.endswith(suffix)
                for suffix in ("csv", "json", "parquet", "orc", "table", "load")
            ):
                dataset, note = self._extract_arg_value(
                    node,
                    0,
                    {"path", "tableName"},
                    string_bindings,
                )
                event = self._build_read_event(
                    source_file=relative,
                    line=node.lineno,
                    source_dataset=dataset,
                    transformation_type=f"python:pyspark_read_{call_name.split('.')[-1]}",
                    note=note,
                )
                events.append(event)

            # PySpark writes
            elif ".write." in call_name and any(
                call_name.endswith(suffix)
                for suffix in ("csv", "json", "parquet", "orc", "save", "saveAsTable")
            ):
                dataset, note = self._extract_arg_value(
                    node,
                    0,
                    {"path", "name", "tableName"},
                    string_bindings,
                )
                event = TransformationEvent(
                    source_datasets=[f"python_runtime:{relative}"],
                    target_datasets=[dataset or "dynamic reference, cannot resolve"],
                    transformation_type=f"python:pyspark_write_{call_name.split('.')[-1]}",
                    source_file=relative,
                    line_range=(node.lineno, getattr(node, "end_lineno", node.lineno)),
                    notes=[note] if note else [],
                )
                events.append(event)

        for event in events:
            if any(item == "dynamic reference, cannot resolve" for item in event.source_datasets + event.target_datasets):
                warnings.append(
                    f"{event.source_file}:{event.line_range[0] if event.line_range else '?'} dynamic reference, cannot resolve"
                )

        return AnalyzerResult(events=events, warnings=warnings)

    def _build_read_event(
        self,
        source_file: str,
        line: int,
        source_dataset: str | None,
        transformation_type: str,
        note: str | None,
    ) -> TransformationEvent:
        return TransformationEvent(
            source_datasets=[source_dataset or "dynamic reference, cannot resolve"],
            target_datasets=[f"python_runtime:{source_file}"],
            transformation_type=transformation_type,
            source_file=source_file,
            line_range=(line, line),
            notes=[note] if note else [],
        )

    def _call_name(self, func: ast.AST) -> str:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            left = self._call_name(func.value)
            return f"{left}.{func.attr}" if left else func.attr
        return ""

    def _extract_arg_value(
        self,
        call: ast.Call,
        position: int,
        keyword_names: set[str],
        string_bindings: dict[str, str],
    ) -> tuple[str | None, str | None]:
        target: ast.AST | None = None
        if len(call.args) > position:
            target = call.args[position]
        else:
            for kw in call.keywords:
                if kw.arg in keyword_names:
                    target = kw.value
                    break

        if target is None:
            return None, None

        return self._resolve_string_node(target, string_bindings)

    def _collect_string_bindings(self, tree: ast.AST) -> dict[str, str]:
        """Collect straightforward variable -> string bindings for light name resolution."""
        bindings: dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                resolved, note = self._resolve_string_node(node.value, bindings)
                if resolved and not note:
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            bindings[target.id] = resolved
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.value is not None:
                    resolved, note = self._resolve_string_node(node.value, bindings)
                    if resolved and not note:
                        bindings[node.target.id] = resolved
        return bindings

    def _resolve_string_node(
        self,
        node: ast.AST,
        string_bindings: dict[str, str],
    ) -> tuple[str | None, str | None]:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value, None

        if isinstance(node, ast.Name):
            if node.id in string_bindings:
                return string_bindings[node.id], None
            return None, "dynamic reference, cannot resolve"

        if isinstance(node, ast.JoinedStr):
            parts: list[str] = []
            for value in node.values:
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    parts.append(value.value)
                else:
                    return None, "dynamic reference, cannot resolve"
            return "".join(parts), None

        return None, "dynamic reference, cannot resolve"

    def _extract_tables_from_sql(self, sql_text: str) -> list[str]:
        tables: set[str] = set()
        for dialect in self.DIALECTS:
            try:
                parsed = sqlglot.parse_one(sql_text, read=dialect)
                for table in parsed.find_all(exp.Table):
                    table_name = table.sql(dialect=dialect)
                    if table_name:
                        tables.add(table_name)
                if tables:
                    break
            except Exception:
                continue
        return sorted(tables)
