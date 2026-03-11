from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from src.agents.hydrologist import HydrologistAgent
from src.agents.surveyor import SurveyorAgent


class AnalysisOrchestrator:
    def __init__(self, artifact_root: Path) -> None:
        self.artifact_root = artifact_root.resolve()

    def run(self, target: str, days: int = 30) -> dict:
        repo_path, temp_dir = self._resolve_target_repo(target)
        try:
            surveyor = SurveyorAgent(repo_path)
            surveyor_result = surveyor.run(days=days, output_root=self.artifact_root)

            hydrologist = HydrologistAgent(repo_path)
            hydrologist_result = hydrologist.run(output_root=self.artifact_root)

            return {
                "target": target,
                "resolved_repo": str(repo_path),
                "surveyor": surveyor_result,
                "hydrologist": hydrologist_result,
            }
        finally:
            if temp_dir is not None and temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

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
