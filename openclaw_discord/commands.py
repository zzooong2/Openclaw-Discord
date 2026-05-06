from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CommandKind(str, Enum):
    MODE = "mode"
    APP = "app"
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    CONFIRMATION = "confirmation"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Command:
    kind: CommandKind
    action: str
    payload: dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""


EXACT_COMMANDS: dict[str, Command] = {
    "클로 온": Command(CommandKind.MODE, "set", {"enabled": True}),
    "클로 오프": Command(CommandKind.MODE, "set", {"enabled": False}),
    "확인": Command(CommandKind.CONFIRMATION, "confirm"),
    "취소": Command(CommandKind.CONFIRMATION, "cancel"),
    "메모장 열어": Command(CommandKind.APP, "open", {"target": "notepad"}),
    "계산기 열어": Command(CommandKind.APP, "open", {"target": "calculator"}),
    "크롬 열어": Command(CommandKind.APP, "open", {"target": "chrome"}),
    "파일 탐색기 열어": Command(CommandKind.APP, "open", {"target": "explorer"}),
    "메모장 닫아": Command(CommandKind.APP, "close", {"target": "notepad", "requires_confirmation": True}),
    "계산기 닫아": Command(CommandKind.APP, "close", {"target": "calculator", "requires_confirmation": True}),
    "크롬 닫아": Command(CommandKind.APP, "close", {"target": "chrome", "requires_confirmation": True}),
    "파일 탐색기 닫아": Command(CommandKind.APP, "close", {"target": "explorer", "requires_confirmation": True}),
    "창 닫아": Command(CommandKind.APP, "close_active_window", {"requires_confirmation": True}),
    "마우스 위로": Command(CommandKind.MOUSE, "move_relative", {"dx": 0, "dy": -1, "step": "default"}),
    "마우스 아래로": Command(CommandKind.MOUSE, "move_relative", {"dx": 0, "dy": 1, "step": "default"}),
    "마우스 왼쪽으로": Command(CommandKind.MOUSE, "move_relative", {"dx": -1, "dy": 0, "step": "default"}),
    "마우스 오른쪽으로": Command(CommandKind.MOUSE, "move_relative", {"dx": 1, "dy": 0, "step": "default"}),
    "마우스 조금 위로": Command(CommandKind.MOUSE, "move_relative", {"dx": 0, "dy": -1, "step": "small"}),
    "마우스 조금 아래로": Command(CommandKind.MOUSE, "move_relative", {"dx": 0, "dy": 1, "step": "small"}),
    "마우스 조금 왼쪽으로": Command(CommandKind.MOUSE, "move_relative", {"dx": -1, "dy": 0, "step": "small"}),
    "마우스 조금 오른쪽으로": Command(CommandKind.MOUSE, "move_relative", {"dx": 1, "dy": 0, "step": "small"}),
    "마우스 가운데로": Command(CommandKind.MOUSE, "move_position", {"position": "center"}),
    "마우스 왼쪽 위로": Command(CommandKind.MOUSE, "move_position", {"position": "top_left"}),
    "마우스 오른쪽 위로": Command(CommandKind.MOUSE, "move_position", {"position": "top_right"}),
    "마우스 왼쪽 아래로": Command(CommandKind.MOUSE, "move_position", {"position": "bottom_left"}),
    "마우스 오른쪽 아래로": Command(CommandKind.MOUSE, "move_position", {"position": "bottom_right"}),
    "왼쪽 클릭": Command(CommandKind.MOUSE, "click", {"button": "left"}),
    "오른쪽 클릭": Command(CommandKind.MOUSE, "click", {"button": "right"}),
    "더블 클릭": Command(CommandKind.MOUSE, "double_click"),
    "엔터": Command(CommandKind.KEYBOARD, "press", {"key": "enter"}),
    "이스케이프": Command(CommandKind.KEYBOARD, "press", {"key": "escape"}),
    "복사": Command(CommandKind.KEYBOARD, "shortcut", {"keys": ("ctrl", "c")}),
    "붙여넣기": Command(CommandKind.KEYBOARD, "shortcut", {"keys": ("ctrl", "v")}),
    "잘라내기": Command(CommandKind.KEYBOARD, "shortcut", {"keys": ("ctrl", "x")}),
    "모두 선택": Command(CommandKind.KEYBOARD, "shortcut", {"keys": ("ctrl", "a")}),
    "실행 취소": Command(CommandKind.KEYBOARD, "shortcut", {"keys": ("ctrl", "z")}),
    "다시 실행": Command(CommandKind.KEYBOARD, "shortcut", {"keys": ("ctrl", "y")}),
    "창 전환": Command(CommandKind.KEYBOARD, "shortcut", {"keys": ("alt", "tab")}),
}


def parse_command(text: str, *, max_text_input_chars: int = 40) -> Command:
    normalized = " ".join(text.strip().split())
    if normalized in EXACT_COMMANDS:
        command = EXACT_COMMANDS[normalized]
        return Command(command.kind, command.action, dict(command.payload), normalized)

    suffix = " 입력"
    if normalized.endswith(suffix):
        text_to_type = normalized[: -len(suffix)].strip()
        if 0 < len(text_to_type) <= max_text_input_chars:
            return Command(CommandKind.KEYBOARD, "type_text", {"text": text_to_type}, normalized)

    return Command(CommandKind.UNKNOWN, "unknown", {"text": normalized}, normalized)

