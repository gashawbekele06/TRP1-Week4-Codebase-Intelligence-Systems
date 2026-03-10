from __future__ import annotations

import ast
from pathlib import Path

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

        For Phase 1, import/function/class extraction is implemented for Python.
        Other supported languages are recognized through LanguageRouter and returned
        with empty symbol data.
        """
        module_path = Path(path)
        if not module_path.is_absolute():
            module_path = (self.repo_root / module_path).resolve()

        language = self.router.get_language_for_path(module_path) or "unknown"
        node = ModuleNode(path=str(module_path.relative_to(self.repo_root)), language=language)

        parser = self.router.get_parser_for_path(module_path)
        if parser is not None:
            # Parse pass ensures tree-sitter grammar availability and syntactic validity.
            parser.parse(module_path.read_bytes())

        if language == "python":
            self._populate_python_symbols(module_path, node)

        return node

    def _populate_python_symbols(self, module_path: Path, node: ModuleNode) -> None:
        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        imports: list[str] = []
        functions: list[FunctionInfo] = []
        classes: list[ClassInfo] = []

        for stmt in tree.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    imports.append(alias.name)

            elif isinstance(stmt, ast.ImportFrom):
                module = stmt.module or ""
                if stmt.level > 0:
                    module = self._resolve_relative_import(module_path, stmt.level, module)
                if module:
                    imports.append(module)

            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                normalized = stmt.name.lstrip("_")
                if normalized and not normalized.startswith("__"):
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

        node.imports = sorted(set(imports))
        node.public_functions = functions
        node.classes = classes

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
