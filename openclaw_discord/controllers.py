from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from openclaw_discord.commands import Command


class Controller(Protocol):
    def execute(self, command: Command) -> str | None:
        """Execute an already approved command."""


@dataclass
class RecordedController:
    calls: list[Command] = field(default_factory=list)

    def execute(self, command: Command) -> str | None:
        self.calls.append(command)
        return None


class DryRunController:
    def execute(self, command: Command) -> str | None:
        print(f"[DRY-RUN] {command.kind.value}.{command.action} {command.payload}")
        return None
