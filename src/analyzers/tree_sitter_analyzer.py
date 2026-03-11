from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable

from tree_sitter_language_pack import get_parser

from src.models.module import ClassInfo, FunctionInfo, ModuleNode


class LanguageRouter:
    """Routes file extensions to language identifiers and parsers."""

    EXTENSION_TO_LANGUAGE: dict[str, str] = {
        ".py": "python",
        ".sql": "sql",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "tsx",
    }

    def get_language_for_path(self, file_path: Path) -> str | None:
        return self.EXTENSION_TO_LANGUAGE.get(file_path.suffix.lower())

    def get_parser_for_path(self, file_path: Path):
        language = self.get_language_for_path(file_path)
        if not language:
            return None
        try:
            return get_parser(language)
        except Exception:
            return None


class TreeSitterAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.router = LanguageRouter()

    def analyze_module(self, path: str | Path) -> ModuleNode:
        """Return a ModuleNode with imports, public functions, and classes.

        Structural extraction uses language-aware routing:
        - Python: imports, public functions, classes (AST with tree-sitter fallback)
        - SQL: table references and CTE-style structures via tree-sitter
        - YAML: dependency/topology-like keys via tree-sitter
        """
        module_path = Path(path)
        if not module_path.is_absolute():
            module_path = (self.repo_root / module_path).resolve()

        language = self.router.get_language_for_path(module_path) or "unknown"
        try:
            module_rel_path = str(module_path.relative_to(self.repo_root))
        except ValueError:
            module_rel_path = module_path.name

        node = ModuleNode(path=module_rel_path, language=language)

        try:
            source_bytes = module_path.read_bytes()
        except OSError:
            return node

        tree = None
        parser = self.router.get_parser_for_path(module_path)
        if parser is not None:
            try:
                tree = parser.parse(source_bytes)
            except Exception:
                tree = None

        try:
            if language == "python":
                self._populate_python_symbols(module_path, node, source_bytes, tree)
            elif language == "sql":
                self._populate_sql_symbols(node, source_bytes, tree)
            elif language == "yaml":
                self._populate_yaml_symbols(node, source_bytes, tree)
        except Exception:
            # Keep per-file analysis resilient; one malformed AST should not fail the run.
            return node

        return node

    def _populate_python_symbols(
        self,
        module_path: Path,
        node: ModuleNode,
        source_bytes: bytes,
        ts_tree,
    ) -> None:
        source = source_bytes.decode("utf-8", errors="replace")
        try:
            parsed = ast.parse(source)
        except SyntaxError:
            if ts_tree is not None:
                self._populate_python_symbols_from_tree_sitter(node, source_bytes, ts_tree)
            return

        imports: set[str] = set()
        functions: list[FunctionInfo] = []
        classes: list[ClassInfo] = []

        for stmt in ast.walk(parsed):
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    imports.add(alias.name)

            elif isinstance(stmt, ast.ImportFrom):
                base_module = stmt.module or ""
                if stmt.level > 0:
                    base_module = self._resolve_relative_import(module_path, stmt.level, base_module)
                if base_module:
                    imports.add(base_module)

                for alias in stmt.names:
                    if alias.name == "*":
                        continue
                    imports.add(f"{base_module}.{alias.name}" if base_module else alias.name)

        for stmt in parsed.body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                normalized = stmt.name.lstrip("_")
                is_decorated = bool(stmt.decorator_list)
                if normalized and not normalized.startswith("__") and (is_decorated or not stmt.name.startswith("_")):
                    functions.append(
                        FunctionInfo(
                            name=stmt.name,
                            normalized_name=normalized,
                            line_start=getattr(stmt, "lineno", None),
                            line_end=getattr(stmt, "end_lineno", None),
                        )
                    )

            elif isinstance(stmt, ast.ClassDef):
                bases: list[str] = []
                for base in stmt.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        parts: list[str] = []
                        current = base
                        while isinstance(current, ast.Attribute):
                            parts.append(current.attr)
                            current = current.value
                        if isinstance(current, ast.Name):
                            parts.append(current.id)
                        bases.append(".".join(reversed(parts)))
                    else:
                        bases.append(ast.unparse(base))

                classes.append(
                    ClassInfo(
                        name=stmt.name,
                        bases=bases,
                        line_start=getattr(stmt, "lineno", None),
                        line_end=getattr(stmt, "end_lineno", None),
                    )
                )

        node.imports = sorted(imports)
        node.public_functions = functions
        node.classes = classes

    def _populate_python_symbols_from_tree_sitter(self, node: ModuleNode, source_bytes: bytes, ts_tree) -> None:
        imports: set[str] = set()
        functions: list[FunctionInfo] = []
        classes: list[ClassInfo] = []

        for current in self._iter_nodes(ts_tree.root_node):
            if current.type in {"import_statement", "import_from_statement"}:
                imports.update(self._extract_python_imports_from_node(current, source_bytes))

            elif current.type == "function_definition":
                name_node = self._first_child_of_type(current, "identifier")
                if name_node is None:
                    continue
                name = self._node_text(source_bytes, name_node)
                normalized = name.lstrip("_")
                if normalized and not normalized.startswith("__"):
                    functions.append(
                        FunctionInfo(
                            name=name,
                            normalized_name=normalized,
                            line_start=name_node.start_point[0] + 1,
                            line_end=current.end_point[0] + 1,
                        )
                    )

            elif current.type == "class_definition":
                name_node = self._first_child_of_type(current, "identifier")
                if name_node is None:
                    continue
                bases = []
                arg_list = self._first_child_of_type(current, "argument_list")
                if arg_list is not None:
                    for arg in arg_list.named_children:
                        text = self._node_text(source_bytes, arg)
                        if text:
                            bases.append(text)
                classes.append(
                    ClassInfo(
                        name=self._node_text(source_bytes, name_node),
                        bases=bases,
                        line_start=name_node.start_point[0] + 1,
                        line_end=current.end_point[0] + 1,
                    )
                )

        node.imports = sorted(imports)
        node.public_functions = functions
        node.classes = classes

    def _extract_python_imports_from_node(self, current, source_bytes: bytes) -> set[str]:
        text = self._node_text(source_bytes, current)
        imports: set[str] = set()
        for raw_part in text.split(","):
            part = raw_part.strip()
            if not part:
                continue
            if part.startswith("import "):
                imports.add(part.removeprefix("import ").strip().split(" as ")[0].strip())
            elif part.startswith("from ") and " import " in part:
                module_part, imported_part = part.removeprefix("from ").split(" import ", maxsplit=1)
                module_part = module_part.strip()
                imported_part = imported_part.strip()
                if module_part:
                    imports.add(module_part)
                for imported in imported_part.split(","):
                    imported_name = imported.strip().split(" as ")[0].strip()
                    if imported_name and imported_name != "*":
                        imports.add(f"{module_part}.{imported_name}" if module_part else imported_name)
        return imports

    def _populate_sql_symbols(self, node: ModuleNode, source_bytes: bytes, ts_tree) -> None:
        if ts_tree is None:
            return

        imports: set[str] = set()
        ctes: list[FunctionInfo] = []
        sql_stopwords = {
            "from",
            "join",
            "on",
            "as",
            "select",
            "where",
            "group",
            "order",
            "by",
            "inner",
            "left",
            "right",
            "full",
            "cross",
            "with",
            "and",
            "or",
        }

        for current in self._iter_nodes(ts_tree.root_node):
            lowered_type = current.type.lower()
            if any(
                marker in lowered_type
                for marker in ("from", "join", "table", "relation", "object_reference")
            ):
                for ident in self._descendants_with_type_fragment(
                    current,
                    ("identifier", "object", "table", "name", "relation", "reference"),
                ):
                    text = self._clean_reference(self._node_text(source_bytes, ident))
                    if not text:
                        continue
                    lowered_text = text.lower()
                    if lowered_text in sql_stopwords:
                        continue
                    if any(ch in text for ch in "()=><"):
                        continue
                    if lowered_text.isdigit():
                        continue
                    if self._looks_like_sql_alias_or_column(text):
                        continue
                    imports.add(self._normalize_sql_reference(text))

            if current.type in {"cte", "common_table_expression"}:
                name_node = self._first_descendant_with_type_fragment(current, ("identifier", "name"))
                if name_node is not None:
                    cte_name = self._clean_reference(self._node_text(source_bytes, name_node))
                    if cte_name:
                        ctes.append(
                            FunctionInfo(
                                name=cte_name,
                                normalized_name=cte_name,
                                line_start=name_node.start_point[0] + 1,
                                line_end=current.end_point[0] + 1,
                            )
                        )

        node.imports = sorted(self._dedupe_sql_references(imports))
        node.public_functions = ctes

    def _looks_like_sql_alias_or_column(self, value: str) -> bool:
        token = value.strip().strip("\"'`")
        if not token:
            return True

        lowered = token.lower()
        if lowered in {"t", "u", "o", "a", "b", "c"}:
            return True

        # Very short bare identifiers are often aliases in JOIN predicates.
        if len(token) <= 2 and "." not in token:
            return True

        # Likely column names (id/user_id/etc.) should not be treated as table refs.
        if "_id" in lowered or lowered.endswith("id"):
            return True

        # Prefer table-like objects: schema.table or plural/object-ish identifiers.
        if "." in token:
            return False

        return not (lowered.endswith("s") or lowered.endswith("table"))

    def _normalize_sql_reference(self, value: str) -> str:
        token = value.strip().strip("\"'`")
        # Strip trailing alias from forms like "schema.table t".
        if " " in token:
            first, *_ = token.split()
            token = first
        return token

    def _dedupe_sql_references(self, refs: set[str]) -> set[str]:
        # Keep fully-qualified names and drop bare duplicates when possible.
        normalized = {self._normalize_sql_reference(ref) for ref in refs if ref}
        qualified = {ref for ref in normalized if "." in ref}
        if not qualified:
            return normalized

        qualified_suffixes = {ref.split(".")[-1] for ref in qualified}
        return {
            ref
            for ref in normalized
            if "." in ref or ref not in qualified_suffixes
        }

    def _populate_yaml_symbols(self, node: ModuleNode, source_bytes: bytes, ts_tree) -> None:
        if ts_tree is None:
            return

        imports: set[str] = set()
        symbols: list[FunctionInfo] = []

        dependency_keys = {
            "depends_on",
            "upstream",
            "requires",
            "needs",
            "imports",
            "include",
            "includes",
            "refs",
            "ref",
            "sources",
            "source",
        }
        structural_keys = {"tasks", "models", "jobs", "pipelines", "steps"}

        for current in self._iter_nodes(ts_tree.root_node):
            if "pair" not in current.type and "mapping" not in current.type:
                continue
            named = [child for child in current.named_children]
            if len(named) < 2:
                continue

            key_text = self._clean_reference(self._node_text(source_bytes, named[0]).strip("\"' "))
            value_node = named[1]

            if key_text in dependency_keys:
                imports.update(self._extract_yaml_values(value_node, source_bytes))

            if key_text in structural_keys:
                for entry in self._extract_yaml_values(value_node, source_bytes):
                    if not entry:
                        continue
                    symbols.append(
                        FunctionInfo(
                            name=entry,
                            normalized_name=entry,
                            line_start=value_node.start_point[0] + 1,
                            line_end=value_node.end_point[0] + 1,
                        )
                    )

            if key_text in {"id", "name"}:
                value_text = self._clean_reference(self._node_text(source_bytes, value_node).strip("\"' "))
                if value_text:
                    symbols.append(
                        FunctionInfo(
                            name=value_text,
                            normalized_name=value_text,
                            line_start=value_node.start_point[0] + 1,
                            line_end=value_node.end_point[0] + 1,
                        )
                    )

        node.imports = sorted(item for item in imports if item)
        seen = set()
        deduped: list[FunctionInfo] = []
        for item in symbols:
            if item.name in seen:
                continue
            seen.add(item.name)
            deduped.append(item)
        node.public_functions = deduped

    def _extract_yaml_values(self, value_node, source_bytes: bytes) -> set[str]:
        values: set[str] = set()
        skip_values = {
            "id",
            "name",
            "upstream",
            "depends_on",
            "tasks",
            "models",
            "jobs",
            "pipelines",
            "steps",
            "[]",
            "{}",
            "-",
            ":",
        }
        stack = [value_node]
        while stack:
            current = stack.pop()
            if current.named_child_count == 0:
                text = self._clean_reference(self._node_text(source_bytes, current).strip("\"' "))
                if text and text not in skip_values:
                    values.add(text)
                continue
            stack.extend(reversed(current.named_children))
        return values

    def _iter_nodes(self, root) -> Iterable:
        stack = [root]
        while stack:
            current = stack.pop()
            yield current
            if current.named_children:
                stack.extend(reversed(current.named_children))

    def _first_child_of_type(self, node, target_type: str):
        for child in node.named_children:
            if child.type == target_type:
                return child
        return None

    def _descendants_with_type_fragment(self, node, fragments: tuple[str, ...]) -> list:
        matches = []
        for child in self._iter_nodes(node):
            lowered = child.type.lower()
            if any(fragment in lowered for fragment in fragments):
                matches.append(child)
        return matches

    def _first_descendant_with_type_fragment(self, node, fragments: tuple[str, ...]):
        for child in self._iter_nodes(node):
            lowered = child.type.lower()
            if any(fragment in lowered for fragment in fragments):
                return child
        return None

    def _node_text(self, source_bytes: bytes, node) -> str:
        return source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="replace")

    def _clean_reference(self, value: str) -> str:
        cleaned = value.strip().strip("\"'`")
        if cleaned.endswith(","):
            cleaned = cleaned[:-1].strip()
        return cleaned

    def _resolve_relative_import(self, module_path: Path, level: int, module: str) -> str:
        """Resolve Python relative import targets to dotted repo-relative modules."""
        directory = module_path.parent
        for _ in range(level - 1):
            directory = directory.parent

        candidate = directory
        if module:
            candidate = candidate / module.replace(".", "/")

        try:
            relative = candidate.relative_to(self.repo_root)
        except ValueError:
            return module

        dotted = ".".join(relative.parts)
        return dotted.strip(".")
