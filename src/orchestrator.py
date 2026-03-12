from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

from src.agents.archivist import ArchivistAgent
from src.agents.hydrologist import HydrologistAgent
from src.agents.navigator import NavigatorAgent
from src.agents.semanticist import SemanticistAgent
from src.agents.surveyor import SurveyorAgent
from src.tracing import CartographyTracer


class AnalysisOrchestrator:
    def __init__(self, artifact_root: Path) -> None:
        self.artifact_root = artifact_root.resolve()

    def run(self, target: str, days: int = 30) -> dict:
        repo_path, temp_dir = self._resolve_target_repo(target)
        try:
            cartography_root = self.artifact_root / ".cartography"
            tracer = CartographyTracer(cartography_root / "cartography_trace.jsonl")
            incremental_info = self._detect_incremental_scope(repo_path)

            tracer.log(
                agent="Orchestrator",
                action="start_run",
                confidence=0.99,
                analysis_method="static-analysis",
                evidence_sources=[
                    {"file": str(repo_path), "line_range": "L1-L1", "method": "static-analysis"}
                ],
                metadata={"incremental": incremental_info["incremental_mode"]},
            )

            surveyor = SurveyorAgent(repo_path)
            surveyor_result = surveyor.run(
                days=days,
                output_root=self.artifact_root,
                changed_files=incremental_info["changed_files"] if incremental_info["incremental_mode"] else None,
                tracer=tracer,
            )

            hydrologist = HydrologistAgent(repo_path)
            hydrologist_result = hydrologist.run(
                output_root=self.artifact_root,
                changed_files=incremental_info["changed_files"] if incremental_info["incremental_mode"] else None,
                tracer=tracer,
            )

            semanticist = SemanticistAgent(repo_path)
            semanticist_result = semanticist.run(
                surveyor_result=surveyor_result,
                hydrologist_result=hydrologist_result,
                output_root=self.artifact_root,
                changed_files=incremental_info["changed_files"] if incremental_info["incremental_mode"] else None,
                tracer=tracer,
            )

            archivist = ArchivistAgent(repo_path)
            archivist_result = archivist.generate_CODEBASE_md(
                surveyor_result=surveyor_result,
                hydrologist_result=hydrologist_result,
                semanticist_result=semanticist_result,
                output_root=self.artifact_root,
                tracer=tracer,
            )

            navigator = NavigatorAgent(self.artifact_root, tracer=tracer)
            navigator_path = str((self.artifact_root / ".cartography" / "navigator_agent.json").resolve())
            self._write_navigator_manifest(navigator_path)

            self._persist_run_state(repo_path, incremental_info.get("head_commit"))

            tracer.log(
                agent="Orchestrator",
                action="finish_run",
                confidence=0.99,
                analysis_method="static-analysis",
                evidence_sources=[
                    {"file": archivist_result["codebase_md_path"], "line_range": "L1-L220", "method": "hybrid-static-llm"}
                ],
                metadata={
                    "incremental": incremental_info["incremental_mode"],
                    "changed_files_count": len(incremental_info.get("changed_files", [])),
                },
            )

            return {
                "target": target,
                "resolved_repo": str(repo_path),
                "incremental": incremental_info,
                "surveyor": surveyor_result,
                "hydrologist": hydrologist_result,
                "semanticist": semanticist_result,
                "archivist": archivist_result,
                "navigator": {
                    "status": "ready",
                    "manifest_path": navigator_path,
                    "agent_class": navigator.__class__.__name__,
                },
                "trace": {
                    "path": str((self.artifact_root / ".cartography" / "cartography_trace.jsonl").resolve())
                },
            }
        finally:
            if temp_dir is not None and temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _detect_incremental_scope(self, repo_path: Path) -> dict:
        head_commit = self._head_commit(repo_path)
        last_commit = self._load_last_commit(repo_path)
        if not head_commit or not last_commit or head_commit == last_commit:
            return {
                "incremental_mode": False,
                "changed_files": [],
                "head_commit": head_commit,
                "last_commit": last_commit,
            }

        changed_files = self._changed_files(repo_path, last_commit, head_commit)
        if not changed_files:
            return {
                "incremental_mode": False,
                "changed_files": [],
                "head_commit": head_commit,
                "last_commit": last_commit,
            }

        return {
            "incremental_mode": True,
            "changed_files": changed_files,
            "head_commit": head_commit,
            "last_commit": last_commit,
        }

    def _state_path(self) -> Path:
        return self.artifact_root / ".cartography" / "run_state.json"

    def _load_last_commit(self, repo_path: Path) -> str | None:
        state_path = self._state_path()
        if not state_path.exists():
            return None
        try:
            payload = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return payload.get("repos", {}).get(str(repo_path.resolve()), {}).get("last_commit")

    def _persist_run_state(self, repo_path: Path, head_commit: str | None) -> None:
        if not head_commit:
            return
        state_path = self._state_path()
        state_path.parent.mkdir(parents=True, exist_ok=True)

        payload: dict = {"repos": {}}
        if state_path.exists():
            try:
                payload = json.loads(state_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                payload = {"repos": {}}

        repos = payload.setdefault("repos", {})
        repos[str(repo_path.resolve())] = {
            "last_commit": head_commit,
            "updated_at_utc": datetime.now(UTC).isoformat(),
        }
        state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _head_commit(self, repo_path: Path) -> str | None:
        cmd = ["git", "-C", str(repo_path), "rev-parse", "HEAD"]
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError:
            return None
        return result.stdout.strip() or None

    def _changed_files(self, repo_path: Path, old_commit: str, new_commit: str) -> list[str]:
        cmd = ["git", "-C", str(repo_path), "diff", "--name-only", old_commit, new_commit]
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError:
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def _write_navigator_manifest(self, manifest_path: str) -> None:
        path = Path(manifest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "agent": "Navigator",
            "framework": "LangGraph (fallback pipeline when unavailable)",
            "tools": [
                "module_graph_lookup",
                "lineage_lookup",
                "semantic_lookup",
                "codebase_lookup",
            ],
            "citation_policy": "Every answer includes source file, line range, and method attribution.",
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _resolve_target_repo(self, target: str) -> tuple[Path, Path | None]:
        if self._is_url(target):
            tmp_root = Path(tempfile.mkdtemp(prefix="cartographer_repo_"))
            repo_dir = tmp_root / "repo"
            self._clone_repo(target, repo_dir)
            return repo_dir, tmp_root

        return Path(target).resolve(), None

    def _clone_repo(self, url: str, dest: Path) -> None:
        cmd = ["git", "clone", "--depth", "1", url, str(dest)]
        subprocess.run(cmd, check=True, capture_output=True, text=True)

    def _is_url(self, value: str) -> bool:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https", "git"} and bool(parsed.netloc)
