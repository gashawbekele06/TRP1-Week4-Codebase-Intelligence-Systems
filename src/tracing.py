from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class CartographyTracer:
    trace_path: Path

    def __post_init__(self) -> None:
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        *,
        agent: str,
        action: str,
        confidence: float,
        analysis_method: str,
        evidence_sources: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        event = {
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "agent": agent,
            "action": action,
            "confidence": round(float(confidence), 4),
            "analysis_method": analysis_method,
            "evidence_sources": evidence_sources or [],
            "metadata": metadata or {},
        }
        with self.trace_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
