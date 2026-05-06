from __future__ import annotations

from dataclasses import dataclass, field


EMERGENCY_HOTKEY = "ctrl+alt+f12"


@dataclass(frozen=True)
class InputBlockEvent:
    device: str
    name: str


@dataclass
class SimulatedInputBlocker:
    enabled: bool = False
    events: list[InputBlockEvent] = field(default_factory=list)

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    def record_event(self, event: InputBlockEvent) -> bool:
        if event.device == "keyboard" and event.name.lower() == EMERGENCY_HOTKEY:
            return False

        if not self.enabled:
            return False

        self.events.append(event)
        return True

