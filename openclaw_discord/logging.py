from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TEXT_TAGS = {
    "voice_command": "VOICE",
    "success": "OK",
    "failure": "FAIL",
    "blocked": "BLOCKED",
}


@dataclass(frozen=True)
class LogEvent:
    type: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class OpenClawLogger:
    def __init__(self, log_dir: str | Path) -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.log_dir / "openclaw.jsonl"
        self.text_path = self.log_dir / "openclaw.log"

    def write(self, event: LogEvent) -> None:
        with self.jsonl_path.open("a", encoding="utf-8") as jsonl_file:
            jsonl_file.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")

        tag = TEXT_TAGS.get(event.type, event.type.upper())
        with self.text_path.open("a", encoding="utf-8") as text_file:
            text_file.write(f"{event.timestamp} [{tag}] {event.message}\n")

