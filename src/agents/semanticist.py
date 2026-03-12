from __future__ import annotations

import ast
import json
import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request


@dataclass
class ModuleSemanticRecord:
    path: str
    language: str
    purpose_statement: str
    docstring: str | None
    docstring_contradiction: bool
    contradiction_reason: str | None
    inferred_domain: str
    evidence: list[str]


class OpenRouterClient:
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, app_name: str = "Brownfield Cartographer") -> None:
        self.api_key = api_key
        self.app_name = app_name

    def generate_json(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1200,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        payload = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        data = json.dumps(payload).encode("utf-8")

        req = request.Request(
            self.BASE_URL,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://local.cartographer",
                "X-Title": self.app_name,
            },
            method="POST",
        )

        with request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8")

        payload = json.loads(body)
        content = payload["choices"][0]["message"]["content"]
        return json.loads(content)


class SemanticistAgent:
    ANALYZABLE_SUFFIXES = {".py", ".sql", ".yml", ".yaml", ".js", ".jsx", ".ts", ".tsx", ".md"}
    DEFAULT_FAST_MODEL = "google/gemini-2.0-flash-001"
    DEFAULT_SYNTHESIS_MODEL = "mistralai/mistral-large-latest"

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.warnings: list[str] = []

        self._hydrate_env_file()
        self.fast_model = os.getenv("OPENROUTER_FAST_MODEL", self.DEFAULT_FAST_MODEL)
        self.synthesis_model = os.getenv("OPENROUTER_SYNTHESIS_MODEL", self.DEFAULT_SYNTHESIS_MODEL)
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()

        self.client: OpenRouterClient | None = None
        if self.api_key and "your_openrouter" not in self.api_key.lower():
            self.client = OpenRouterClient(self.api_key)
        else:
            self.warnings.append(
                "OPENROUTER_API_KEY not configured; Semanticist is running in heuristic mode."
            )

    def run(
        self,
        *,
        surveyor_result: dict,
        hydrologist_result: dict,
        output_root: Path | None = None,
    ) -> dict:
        records = self._analyze_modules_semantics()
        domain_boundaries = self._cluster_domains(records)
        fde_answers = self._synthesize_fde_answers(records, domain_boundaries, surveyor_result, hydrologist_result)

        output_base = output_root.resolve() if output_root else self.repo_root
        output_path = output_base / ".cartography" / "semantic_report.json"
        self._write_report(output_path, records, domain_boundaries, fde_answers)

        return {
            "module_count": len(records),
            "domain_count": len(domain_boundaries),
            "domain_boundaries": domain_boundaries,
            "warnings": self.warnings,
            "semantic_report_path": str(output_path),
            "five_fde_answers": fde_answers,
            "model_policy": {
                "bulk_extraction_model": self.fast_model,
                "synthesis_model": self.synthesis_model,
            },
        }

    def _hydrate_env_file(self) -> None:
        env_file = self.repo_root / ".env"
        if not env_file.exists():
            return

        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

    def _analyze_modules_semantics(self) -> list[ModuleSemanticRecord]:
        records: list[ModuleSemanticRecord] = []
        for path in sorted(self.repo_root.rglob("*")):
            if not path.is_file():
                continue
            if ".git" in path.parts or ".venv" in path.parts or ".cartography" in path.parts:
                continue
            if path.suffix.lower() not in self.ANALYZABLE_SUFFIXES:
                continue

            rel_path = path.relative_to(self.repo_root).as_posix()
            language = self._infer_language(path)
            text = self._safe_read(path)
            if not text.strip():
                continue

            docstring = self._extract_module_docstring(text) if language == "python" else None
            evidence = self._extract_evidence(path, text, language)

            semantic_result = self._infer_module_purpose(
                rel_path=rel_path,
                language=language,
                docstring=docstring,
                evidence=evidence,
                content=text,
            )

            records.append(
                ModuleSemanticRecord(
                    path=rel_path,
                    language=language,
                    purpose_statement=semantic_result["purpose_statement"],
                    docstring=docstring,
                    docstring_contradiction=semantic_result["docstring_contradiction"],
                    contradiction_reason=semantic_result.get("contradiction_reason"),
                    inferred_domain=semantic_result["inferred_domain"],
                    evidence=evidence,
                )
            )

        return records

    def _infer_module_purpose(
        self,
        *,
        rel_path: str,
        language: str,
        docstring: str | None,
        evidence: list[str],
        content: str,
    ) -> dict[str, Any]:
        truncated = content[:3500]
        if self.client is None:
            return self._heuristic_module_semantics(rel_path, language, docstring, evidence)

        system_prompt = (
            "You are a software semantic analyst. Infer purpose from implementation evidence, not comments. "
            "Respond only with JSON."
        )
        user_prompt = json.dumps(
            {
                "module_path": rel_path,
                "language": language,
                "module_docstring": docstring,
                "implementation_evidence": evidence,
                "code_excerpt": truncated,
                "task": {
                    "purpose_statement": "One sentence about what business/technical purpose this module serves.",
                    "docstring_contradiction": "boolean",
                    "contradiction_reason": "short reason or null",
                    "inferred_domain": "single domain label such as ingestion/transformation/serving/monitoring/orchestration/analysis/testing/docs",
                },
            }
        )

        try:
            result = self.client.generate_json(
                model=self.fast_model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=700,
                temperature=0.0,
            )
            return {
                "purpose_statement": str(result.get("purpose_statement") or "Purpose unavailable"),
                "docstring_contradiction": bool(result.get("docstring_contradiction", False)),
                "contradiction_reason": result.get("contradiction_reason"),
                "inferred_domain": str(result.get("inferred_domain") or "analysis").lower(),
            }
        except (TimeoutError, json.JSONDecodeError, error.URLError, error.HTTPError, KeyError, TypeError, ValueError):
            self.warnings.append(f"LLM purpose extraction failed for {rel_path}; used heuristic fallback.")
            return self._heuristic_module_semantics(rel_path, language, docstring, evidence)

    def _heuristic_module_semantics(
        self,
        rel_path: str,
        language: str,
        docstring: str | None,
        evidence: list[str],
    ) -> dict[str, Any]:
        domain = self._heuristic_domain(rel_path, evidence)
        purpose = (
            f"Module {rel_path} contributes to {domain} concerns by defining "
            f"{', '.join(evidence[:3]) if evidence else 'core repository behavior'}."
        )
        contradiction = False
        reason = None

        if docstring and domain not in docstring.lower():
            contradiction = True
            reason = "Module docstring emphasis differs from implementation-derived domain."

        return {
            "purpose_statement": purpose,
            "docstring_contradiction": contradiction,
            "contradiction_reason": reason,
            "inferred_domain": domain,
        }

    def _cluster_domains(self, records: list[ModuleSemanticRecord]) -> list[dict[str, Any]]:
        buckets: dict[str, list[ModuleSemanticRecord]] = defaultdict(list)
        for record in records:
            buckets[record.inferred_domain].append(record)

        clusters: list[dict[str, Any]] = []
        for domain, modules in sorted(buckets.items(), key=lambda item: (-len(item[1]), item[0])):
            clusters.append(
                {
                    "domain": domain,
                    "module_count": len(modules),
                    "modules": [m.path for m in sorted(modules, key=lambda item: item.path)],
                    "sample_purposes": [m.purpose_statement for m in modules[:3]],
                }
            )
        return clusters

    def _synthesize_fde_answers(
        self,
        records: list[ModuleSemanticRecord],
        domains: list[dict[str, Any]],
        surveyor_result: dict,
        hydrologist_result: dict,
    ) -> dict[str, str]:
        if self.client is None:
            return self._heuristic_fde_answers(records, domains, surveyor_result, hydrologist_result)

        records_payload = [
            {
                "path": r.path,
                "purpose": r.purpose_statement,
                "domain": r.inferred_domain,
            }
            for r in records
        ]
        user_prompt = json.dumps(
            {
                "surveyor": surveyor_result,
                "hydrologist": hydrologist_result,
                "semantic_modules": records_payload,
                "semantic_domains": domains,
                "task": "Generate concise, evidence-grounded answers for the five FDE day-one questions as a JSON object with keys q1..q5.",
            }
        )

        try:
            result = self.client.generate_json(
                model=self.synthesis_model,
                system_prompt=(
                    "You are a principal engineer producing day-one architecture guidance. "
                    "Ground all claims in provided evidence and return only JSON."
                ),
                user_prompt=user_prompt,
                max_tokens=1400,
                temperature=0.1,
            )
            return {
                "q1_primary_ingestion_path": str(result.get("q1") or "Unavailable"),
                "q2_critical_outputs": str(result.get("q2") or "Unavailable"),
                "q3_blast_radius": str(result.get("q3") or "Unavailable"),
                "q4_logic_concentration": str(result.get("q4") or "Unavailable"),
                "q5_git_velocity_map": str(result.get("q5") or "Unavailable"),
            }
        except (TimeoutError, json.JSONDecodeError, error.URLError, error.HTTPError, KeyError, TypeError, ValueError):
            self.warnings.append("LLM synthesis failed for FDE answers; used heuristic fallback.")
            return self._heuristic_fde_answers(records, domains, surveyor_result, hydrologist_result)

    def _heuristic_fde_answers(
        self,
        records: list[ModuleSemanticRecord],
        domains: list[dict[str, Any]],
        surveyor_result: dict,
        hydrologist_result: dict,
    ) -> dict[str, str]:
        top_outputs = hydrologist_result.get("sinks", [])[:5]
        top_sources = hydrologist_result.get("sources", [])[:5]
        hot_files = [item.get("path") for item in surveyor_result.get("high_velocity_core", [])[:5]]
        dead_code = surveyor_result.get("dead_code_candidates", [])
        top_domain = domains[0]["domain"] if domains else "analysis"
        module_examples = [r.path for r in records[:3]]

        return {
            "q1_primary_ingestion_path": (
                "Primary ingestion appears to flow from source datasets "
                f"{top_sources if top_sources else 'not explicitly discovered'} into downstream transformations."
            ),
            "q2_critical_outputs": (
                "Most critical outputs are likely terminal lineage sinks "
                f"{top_outputs if top_outputs else 'not explicitly discovered'} and high-centrality modules from Surveyor PageRank."
            ),
            "q3_blast_radius": (
                "Blast radius is highest around sink-producing transformations and architectural hubs; "
                f"recently active files include {hot_files if hot_files else 'none in selected window'}."
            ),
            "q4_logic_concentration": (
                "Business logic is most concentrated in the inferred domain "
                f"'{top_domain}', with representative modules {module_examples}."
            ),
            "q5_git_velocity_map": (
                "Git velocity hot spots are derived from Surveyor high-velocity core: "
                f"{hot_files if hot_files else 'no significant recent churn'}; dead-code candidates identified: {len(dead_code)}."
            ),
        }

    def _write_report(
        self,
        output_path: Path,
        records: list[ModuleSemanticRecord],
        domains: list[dict[str, Any]],
        fde_answers: dict[str, str],
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "module_purpose_statements": [
                {
                    "path": record.path,
                    "language": record.language,
                    "purpose_statement": record.purpose_statement,
                    "docstring": record.docstring,
                    "docstring_contradiction": record.docstring_contradiction,
                    "contradiction_reason": record.contradiction_reason,
                    "inferred_domain": record.inferred_domain,
                    "evidence": record.evidence,
                }
                for record in records
            ],
            "business_domain_boundaries": domains,
            "five_fde_day_one_answers": fde_answers,
            "warnings": self.warnings,
            "model_policy": {
                "bulk_semantics_model": self.fast_model,
                "synthesis_model": self.synthesis_model,
                "bulk_vs_synthesis_strategy": "Use fast model for per-module extraction; reserve larger model for five-answer synthesis.",
            },
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _infer_language(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".py":
            return "python"
        if suffix == ".sql":
            return "sql"
        if suffix in {".yml", ".yaml"}:
            return "yaml"
        if suffix in {".js", ".jsx", ".ts", ".tsx"}:
            return "javascript"
        if suffix == ".md":
            return "markdown"
        return "unknown"

    def _safe_read(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="utf-8", errors="ignore")

    def _extract_module_docstring(self, text: str) -> str | None:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return None
        return ast.get_docstring(tree)

    def _extract_evidence(self, path: Path, text: str, language: str) -> list[str]:
        evidence: list[str] = []
        if language == "python":
            try:
                tree = ast.parse(text)
                for node in tree.body:
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        evidence.append(f"function:{node.name}")
                    elif isinstance(node, ast.ClassDef):
                        evidence.append(f"class:{node.name}")
                    elif isinstance(node, ast.Import):
                        evidence.extend(f"import:{alias.name}" for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        evidence.append(f"import_from:{node.module}")
            except SyntaxError:
                pass

        if not evidence:
            lines = [line.strip() for line in text.splitlines() if line.strip()][:20]
            evidence = [f"line:{line[:80]}" for line in lines[:6]]

        evidence.append(f"file:{path.name}")
        return evidence[:12]

    def _heuristic_domain(self, rel_path: str, evidence: list[str]) -> str:
        combined = f"{rel_path} {' '.join(evidence)}".lower()
        if any(token in combined for token in ("lineage", "sql", "transform", "dbt", "dag")):
            return "transformation"
        if any(token in combined for token in ("read", "extract", "ingest", "source", "loader")):
            return "ingestion"
        if any(token in combined for token in ("graph", "api", "serve", "endpoint", "output")):
            return "serving"
        if any(token in combined for token in ("test", "assert", "validation", "monitor", "warn")):
            return "monitoring"
        if any(token in combined for token in ("cli", "orchestr", "main")):
            return "orchestration"
        if any(token in combined for token in ("readme", "reconnaissance", "docs")):
            return "documentation"
        return "analysis"
