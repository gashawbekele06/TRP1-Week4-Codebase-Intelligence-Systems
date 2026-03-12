from __future__ import annotations

import ast
import json
import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request

import numpy as np


@dataclass
class ModuleSemanticRecord:
    path: str
    language: str
    purpose_statement: str
    docstring: str | None
    documentation_drift: bool
    documentation_drift_reason: str | None
    inferred_domain: str | None
    evidence: list[str]


@dataclass
class ContextWindowBudget:
    max_tokens: int
    max_spend_usd: float
    estimated_tokens_total: int = 0
    actual_input_tokens_total: int = 0
    actual_output_tokens_total: int = 0
    estimated_spend_usd: float = 0.0
    actual_spend_usd: float = 0.0

    MODEL_RATES_PER_1K: dict[str, dict[str, float]] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.MODEL_RATES_PER_1K is None:
            self.MODEL_RATES_PER_1K = {
                "google/gemini-2.0-flash-001": {"input": 0.000075, "output": 0.00030},
                "google/gemini-2.0-flash-lite-001": {"input": 0.000038, "output": 0.00015},
                "anthropic/claude-3.5-sonnet": {"input": 0.00300, "output": 0.01500},
                "anthropic/claude-3.7-sonnet": {"input": 0.00300, "output": 0.01500},
                "openai/gpt-4.1": {"input": 0.01000, "output": 0.03000},
            }

    def estimate_tokens(self, text: str) -> int:
        # Practical approximation used for admission control before model calls.
        return max(1, math.ceil(len(text) / 4))

    def _rates(self, model: str) -> dict[str, float]:
        return self.MODEL_RATES_PER_1K.get(model, {"input": 0.001, "output": 0.003})

    def can_afford(self, *, model: str, estimated_input_tokens: int, estimated_output_tokens: int) -> bool:
        rates = self._rates(model)
        projected_tokens = self.estimated_tokens_total + estimated_input_tokens + estimated_output_tokens
        projected_spend = self.estimated_spend_usd + (
            (estimated_input_tokens / 1000.0) * rates["input"]
            + (estimated_output_tokens / 1000.0) * rates["output"]
        )
        return projected_tokens <= self.max_tokens and projected_spend <= self.max_spend_usd

    def reserve_estimate(self, *, model: str, estimated_input_tokens: int, estimated_output_tokens: int) -> None:
        rates = self._rates(model)
        self.estimated_tokens_total += estimated_input_tokens + estimated_output_tokens
        self.estimated_spend_usd += (
            (estimated_input_tokens / 1000.0) * rates["input"]
            + (estimated_output_tokens / 1000.0) * rates["output"]
        )

    def register_actual_usage(self, *, model: str, prompt_tokens: int, completion_tokens: int) -> None:
        rates = self._rates(model)
        self.actual_input_tokens_total += max(prompt_tokens, 0)
        self.actual_output_tokens_total += max(completion_tokens, 0)
        self.actual_spend_usd += (
            (max(prompt_tokens, 0) / 1000.0) * rates["input"]
            + (max(completion_tokens, 0) / 1000.0) * rates["output"]
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_tokens": self.max_tokens,
            "max_spend_usd": round(self.max_spend_usd, 6),
            "estimated_tokens_total": self.estimated_tokens_total,
            "actual_input_tokens_total": self.actual_input_tokens_total,
            "actual_output_tokens_total": self.actual_output_tokens_total,
            "estimated_spend_usd": round(self.estimated_spend_usd, 6),
            "actual_spend_usd": round(self.actual_spend_usd, 6),
        }


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
    ) -> tuple[dict[str, Any], dict[str, int]]:
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
        usage = payload.get("usage", {})

        parsed: dict[str, Any]
        if isinstance(content, str):
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                parsed = self._extract_first_json_object(content)
        else:
            parsed = content

        return parsed, {
            "prompt_tokens": int(usage.get("prompt_tokens", 0) or 0),
            "completion_tokens": int(usage.get("completion_tokens", 0) or 0),
        }

    def _extract_first_json_object(self, text: str) -> dict[str, Any]:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise json.JSONDecodeError("No JSON object found", text, 0)
        return json.loads(text[start : end + 1])


class SemanticistAgent:
    ANALYZABLE_SUFFIXES = {".py", ".sql", ".yml", ".yaml", ".js", ".jsx", ".ts", ".tsx", ".md"}
    DEFAULT_FAST_MODEL = "google/gemini-2.0-flash-001"
    DEFAULT_SYNTHESIS_MODEL = "anthropic/claude-3.5-sonnet"
    DEFAULT_MAX_TOKENS = 120_000
    DEFAULT_MAX_SPEND_USD = 5.0

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.warnings: list[str] = []

        self._hydrate_env_file()
        self.fast_model = os.getenv("OPENROUTER_FAST_MODEL", self.DEFAULT_FAST_MODEL)
        self.synthesis_model = os.getenv("OPENROUTER_SYNTHESIS_MODEL", self.DEFAULT_SYNTHESIS_MODEL)
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()

        max_tokens = int(os.getenv("SEMANTICIST_MAX_TOKENS", str(self.DEFAULT_MAX_TOKENS)))
        max_spend = float(os.getenv("SEMANTICIST_MAX_SPEND_USD", str(self.DEFAULT_MAX_SPEND_USD)))
        self.context_budget = ContextWindowBudget(max_tokens=max_tokens, max_spend_usd=max_spend)

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
        domain_boundaries = self.cluster_into_domains(records)
        fde_answers = self.answer_day_one_questions(
            records=records,
            domains=domain_boundaries,
            surveyor_result=surveyor_result,
            hydrologist_result=hydrologist_result,
        )

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
                "tiering": "Bulk module purpose extraction uses fast model (Gemini Flash). Synthesis reserves Claude/GPT-4 tier.",
            },
            "context_window_budget": self.context_budget.to_dict(),
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

            semantic_result = self.generate_purpose_statement(
                {
                    "path": rel_path,
                    "language": language,
                    "docstring": docstring,
                    "evidence": evidence,
                    "content": text,
                }
            )

            records.append(
                ModuleSemanticRecord(
                    path=rel_path,
                    language=language,
                    purpose_statement=semantic_result["purpose_statement"],
                    docstring=docstring,
                    documentation_drift=semantic_result["documentation_drift"],
                    documentation_drift_reason=semantic_result.get("documentation_drift_reason"),
                    inferred_domain=None,
                    evidence=evidence,
                )
            )

        return records

    def generate_purpose_statement(self, module_node: dict[str, Any]) -> dict[str, Any]:
        rel_path = str(module_node["path"])
        language = str(module_node["language"])
        docstring = module_node.get("docstring")
        evidence = list(module_node.get("evidence") or [])
        content = str(module_node.get("content") or "")
        truncated = content[:3500]

        if self.client is None:
            return self._heuristic_module_semantics(rel_path, docstring, evidence, content)

        system_prompt = (
            "You are a software semantic analyst. Infer business purpose from implementation evidence, not comments. "
            "Return JSON only."
        )
        user_prompt = json.dumps(
            {
                "module_path": rel_path,
                "language": language,
                "module_docstring": docstring,
                "implementation_evidence": evidence,
                "code_excerpt": truncated,
                "task": {
                    "purpose_statement": "Write exactly 2-3 sentences focused on business function, not implementation detail.",
                    "documentation_drift": "boolean; true when docstring meaning contradicts implementation behavior.",
                    "documentation_drift_reason": "short reason or null",
                },
            }
        )

        estimated_input_tokens = self.context_budget.estimate_tokens(system_prompt + user_prompt)
        estimated_output_tokens = 350
        if not self.context_budget.can_afford(
            model=self.fast_model,
            estimated_input_tokens=estimated_input_tokens,
            estimated_output_tokens=estimated_output_tokens,
        ):
            self.warnings.append(
                f"ContextWindowBudget prevented LLM purpose generation for {rel_path}; used heuristic fallback."
            )
            return self._heuristic_module_semantics(rel_path, docstring, evidence, content)
        self.context_budget.reserve_estimate(
            model=self.fast_model,
            estimated_input_tokens=estimated_input_tokens,
            estimated_output_tokens=estimated_output_tokens,
        )

        try:
            result, usage = self.client.generate_json(
                model=self.fast_model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=700,
                temperature=0.0,
            )
            self.context_budget.register_actual_usage(
                model=self.fast_model,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
            )

            purpose = str(result.get("purpose_statement") or "Purpose unavailable").strip()
            purpose = self._normalize_to_two_or_three_sentences(purpose)

            return {
                "purpose_statement": purpose,
                "documentation_drift": bool(result.get("documentation_drift", False)),
                "documentation_drift_reason": result.get("documentation_drift_reason"),
            }
        except (TimeoutError, json.JSONDecodeError, error.URLError, error.HTTPError, KeyError, TypeError, ValueError):
            self.warnings.append(f"LLM purpose extraction failed for {rel_path}; used heuristic fallback.")
            return self._heuristic_module_semantics(rel_path, docstring, evidence, content)

    def _heuristic_module_semantics(
        self,
        rel_path: str,
        docstring: str | None,
        evidence: list[str],
        content: str,
    ) -> dict[str, Any]:
        key_behaviors = ", ".join(evidence[:3]) if evidence else "core repository behavior"
        purpose = (
            f"This module supports the codebase by owning {key_behaviors}. "
            f"Its business value is enabling consistent system behavior for the capability represented by {Path(rel_path).stem}."
        )
        purpose = self._normalize_to_two_or_three_sentences(purpose)

        drift = False
        reason = None
        if docstring:
            overlap = self._lexical_overlap(docstring, content[:1200])
            if overlap < 0.10:
                drift = True
                reason = "Documentation Drift: module docstring has low semantic overlap with implementation evidence."

        return {
            "purpose_statement": purpose,
            "documentation_drift": drift,
            "documentation_drift_reason": reason,
        }

    def cluster_into_domains(self, records: list[ModuleSemanticRecord]) -> list[dict[str, Any]]:
        if not records:
            return []

        matrix, vocabulary = self._embed_purpose_statements(records)
        k = self._choose_cluster_count(len(records))
        labels, centroids = self._kmeans(matrix, k)

        clusters: list[dict[str, Any]] = []
        for cluster_id in range(k):
            member_indexes = [idx for idx, label in enumerate(labels) if label == cluster_id]
            if not member_indexes:
                continue

            members = [records[idx] for idx in member_indexes]
            domain = self._label_cluster(
                members=members,
                centroid=centroids[cluster_id],
                vocabulary=vocabulary,
            )
            for member in members:
                member.inferred_domain = domain

            clusters.append(
                {
                    "cluster_id": cluster_id,
                    "domain": domain,
                    "module_count": len(members),
                    "modules": [m.path for m in sorted(members, key=lambda item: item.path)],
                    "sample_purposes": [m.purpose_statement for m in members[:3]],
                }
            )

        return sorted(clusters, key=lambda item: (-item["module_count"], item["domain"]))

    def _embed_purpose_statements(
        self,
        records: list[ModuleSemanticRecord],
    ) -> tuple[np.ndarray, list[str]]:
        texts = [f"{record.path} {record.purpose_statement}" for record in records]
        tokenized = [self._tokenize(text) for text in texts]
        vocabulary = sorted({token for tokens in tokenized for token in tokens})
        if not vocabulary:
            return np.ones((len(records), 1), dtype=float), ["general"]

        index = {token: idx for idx, token in enumerate(vocabulary)}
        matrix = np.zeros((len(records), len(vocabulary)), dtype=float)

        for row, tokens in enumerate(tokenized):
            counts: dict[str, int] = {}
            for token in tokens:
                counts[token] = counts.get(token, 0) + 1
            for token, count in counts.items():
                matrix[row, index[token]] = float(count)

        # TF-IDF weighting for semantic separation.
        doc_freq = (matrix > 0).sum(axis=0)
        idf = np.log((1.0 + len(records)) / (1.0 + doc_freq)) + 1.0
        matrix = matrix * idf

        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        matrix = matrix / norms
        return matrix, vocabulary

    def _choose_cluster_count(self, sample_count: int) -> int:
        if sample_count < 5:
            self.warnings.append(
                "Insufficient modules for 5-8 cluster target; using reduced cluster count equal to module count."
            )
            return max(1, sample_count)
        heuristic = int(round(math.sqrt(sample_count)))
        return min(8, max(5, heuristic))

    def _kmeans(self, matrix: np.ndarray, k: int, max_iter: int = 40) -> tuple[np.ndarray, np.ndarray]:
        # Deterministic initialization to keep outputs stable across runs.
        initial_indexes = np.linspace(0, matrix.shape[0] - 1, num=k, dtype=int)
        centroids = matrix[initial_indexes].copy()
        labels = np.zeros(matrix.shape[0], dtype=int)

        for _ in range(max_iter):
            distances = np.linalg.norm(matrix[:, None, :] - centroids[None, :, :], axis=2)
            new_labels = np.argmin(distances, axis=1)
            if np.array_equal(new_labels, labels):
                break
            labels = new_labels

            for cluster_id in range(k):
                members = matrix[labels == cluster_id]
                if len(members) == 0:
                    centroids[cluster_id] = matrix[cluster_id % len(matrix)]
                else:
                    centroids[cluster_id] = members.mean(axis=0)

        return labels, centroids

    def _label_cluster(
        self,
        *,
        members: list[ModuleSemanticRecord],
        centroid: np.ndarray,
        vocabulary: list[str],
    ) -> str:
        # Lightweight, deterministic domain naming from dominant centroid terms.
        top_indexes = np.argsort(centroid)[-6:][::-1]
        top_terms = [vocabulary[idx] for idx in top_indexes if centroid[idx] > 0]
        combined = " ".join(top_terms + [m.path for m in members]).lower()
        return self._heuristic_domain(combined)

    def answer_day_one_questions(
        self,
        *,
        records: list[ModuleSemanticRecord],
        domains: list[dict[str, Any]],
        surveyor_result: dict,
        hydrologist_result: dict,
    ) -> dict[str, str]:
        citations = self._collect_evidence_citations(surveyor_result, hydrologist_result, records)

        if self.client is None:
            return self._heuristic_fde_answers(records, domains, surveyor_result, hydrologist_result, citations)

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
                "evidence_citations": citations,
                "task": (
                    "Generate concise answers for the five FDE day-one questions. "
                    "Every answer must include concrete citation markers in the form [file_path:Lstart-Lend] from evidence_citations. "
                    "Return JSON object with keys q1..q5 only."
                ),
            }
        )

        system_prompt = (
            "You are a principal engineer producing day-one architecture guidance. "
            "Use only provided evidence; include file+line citations in each answer. Return JSON only."
        )

        estimated_input_tokens = self.context_budget.estimate_tokens(system_prompt + user_prompt)
        estimated_output_tokens = 700
        if not self.context_budget.can_afford(
            model=self.synthesis_model,
            estimated_input_tokens=estimated_input_tokens,
            estimated_output_tokens=estimated_output_tokens,
        ):
            self.warnings.append("ContextWindowBudget prevented synthesis model call; used heuristic FDE answers.")
            return self._heuristic_fde_answers(records, domains, surveyor_result, hydrologist_result, citations)
        self.context_budget.reserve_estimate(
            model=self.synthesis_model,
            estimated_input_tokens=estimated_input_tokens,
            estimated_output_tokens=estimated_output_tokens,
        )

        try:
            result, usage = self.client.generate_json(
                model=self.synthesis_model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=1400,
                temperature=0.1,
            )
            self.context_budget.register_actual_usage(
                model=self.synthesis_model,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
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
            return self._heuristic_fde_answers(records, domains, surveyor_result, hydrologist_result, citations)

    def _heuristic_fde_answers(
        self,
        records: list[ModuleSemanticRecord],
        domains: list[dict[str, Any]],
        surveyor_result: dict,
        hydrologist_result: dict,
        citations: list[str],
    ) -> dict[str, str]:
        top_outputs = hydrologist_result.get("sinks", [])[:5]
        top_sources = hydrologist_result.get("sources", [])[:5]
        hot_files = [item.get("path") for item in surveyor_result.get("high_velocity_core", [])[:5]]
        dead_code = surveyor_result.get("dead_code_candidates", [])
        top_domain = domains[0]["domain"] if domains else "analysis"
        module_examples = [r.path for r in records[:3]]
        citation_suffix = f" Evidence: {'; '.join(citations[:3])}" if citations else ""

        return {
            "q1_primary_ingestion_path": (
                "Primary ingestion appears to flow from source datasets "
                f"{top_sources if top_sources else 'not explicitly discovered'} into downstream transformations."
                f"{citation_suffix}"
            ),
            "q2_critical_outputs": (
                "Most critical outputs are likely terminal lineage sinks "
                f"{top_outputs if top_outputs else 'not explicitly discovered'} and high-centrality modules from Surveyor PageRank."
                f"{citation_suffix}"
            ),
            "q3_blast_radius": (
                "Blast radius is highest around sink-producing transformations and architectural hubs; "
                f"recently active files include {hot_files if hot_files else 'none in selected window'}."
                f"{citation_suffix}"
            ),
            "q4_logic_concentration": (
                "Business logic is most concentrated in the inferred domain "
                f"'{top_domain}', with representative modules {module_examples}."
                f"{citation_suffix}"
            ),
            "q5_git_velocity_map": (
                "Git velocity hot spots are derived from Surveyor high-velocity core: "
                f"{hot_files if hot_files else 'no significant recent churn'}; dead-code candidates identified: {len(dead_code)}."
                f"{citation_suffix}"
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
                    "documentation_drift": record.documentation_drift,
                    "documentation_drift_reason": record.documentation_drift_reason,
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
                "bulk_vs_synthesis_strategy": "Use Gemini Flash for per-module purpose extraction; reserve Claude/GPT-4 tier for five-answer synthesis.",
            },
            "context_window_budget": self.context_budget.to_dict(),
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

    def _heuristic_domain(self, combined: str) -> str:
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

    def _normalize_to_two_or_three_sentences(self, text: str) -> str:
        clean = re.sub(r"\s+", " ", text).strip()
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean) if s.strip()]
        if len(sentences) >= 2:
            return " ".join(sentences[:3])
        if len(sentences) == 1:
            return sentences[0] + " It provides business-facing value by enabling reliable downstream decision-making."
        return "Purpose unavailable. It provides business-facing value through system capability support."

    def _lexical_overlap(self, a: str, b: str) -> float:
        a_tokens = set(self._tokenize(a))
        b_tokens = set(self._tokenize(b))
        if not a_tokens or not b_tokens:
            return 0.0
        intersection = len(a_tokens & b_tokens)
        union = len(a_tokens | b_tokens)
        return intersection / union if union else 0.0

    def _tokenize(self, text: str) -> list[str]:
        stopwords = {
            "the",
            "and",
            "for",
            "with",
            "from",
            "this",
            "that",
            "into",
            "module",
            "file",
            "code",
            "data",
            "python",
            "json",
            "return",
            "class",
            "function",
            "agent",
            "analysis",
        }
        raw = re.findall(r"[a-zA-Z_]{3,}", text.lower())
        return [token for token in raw if token not in stopwords]

    def _collect_evidence_citations(
        self,
        surveyor_result: dict,
        hydrologist_result: dict,
        records: list[ModuleSemanticRecord],
    ) -> list[str]:
        citations: list[str] = []

        for item in surveyor_result.get("dead_code_candidates", [])[:10]:
            module = item.get("module")
            line = item.get("line_start")
            if module and line:
                citations.append(f"{module}:L{line}-L{line}")

        for path_score in surveyor_result.get("pagerank", [])[:10]:
            if isinstance(path_score, (list, tuple)) and path_score:
                citations.append(f"{path_score[0]}:L1-L200")

        lineage_path = hydrologist_result.get("lineage_graph_path")
        if lineage_path:
            citations.extend(self._extract_lineage_citations(Path(lineage_path)))

        for record in records[:10]:
            citations.append(f"{record.path}:L1-L200")

        # preserve order while de-duplicating
        seen: set[str] = set()
        uniq: list[str] = []
        for citation in citations:
            if citation not in seen:
                seen.add(citation)
                uniq.append(citation)
        return uniq[:40]

    def _extract_lineage_citations(self, graph_path: Path) -> list[str]:
        if not graph_path.exists():
            return []
        try:
            payload = json.loads(graph_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

        links = payload.get("graph", {}).get("links", [])
        citations: list[str] = []
        for link in links[:20]:
            source_file = link.get("source_file")
            line_range = link.get("line_range")
            if not source_file:
                continue

            start, end = self._normalize_line_range(line_range)
            citations.append(f"{source_file}:L{start}-L{end}")
        return citations

    def _normalize_line_range(self, line_range: Any) -> tuple[int, int]:
        if isinstance(line_range, (list, tuple)) and len(line_range) == 2:
            start = int(line_range[0] or 1)
            end = int(line_range[1] or start)
            return max(1, start), max(start, end)
        if isinstance(line_range, int):
            return max(1, line_range), max(1, line_range)
        return 1, 200
