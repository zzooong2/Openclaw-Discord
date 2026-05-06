from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from openclaw_discord.commands import Command


class Controller(Protocol):
    def execute(self, command: Command) -> None:
        """Execute an already approved command."""


@dataclass
class RecordedController:
    calls: list[Command] = field(default_factory=list)

    def execute(self, command: Command) -> None:
        self.calls.append(command)


class DryRunController:
    def execute(self, command: Command) -> None:
        print(f"[DRY-RUN] {command.kind.value}.{command.action} {command.payload}")

