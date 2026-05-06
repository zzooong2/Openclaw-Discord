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

    natural_command = _parse_natural_command(normalized, max_text_input_chars=max_text_input_chars)
    if natural_command is not None:
        return natural_command

    suffix = " 입력"
    if normalized.endswith(suffix):
        text_to_type = normalized[: -len(suffix)].strip()
        if 0 < len(text_to_type) <= max_text_input_chars:
            return Command(CommandKind.KEYBOARD, "type_text", {"text": text_to_type}, normalized)

    return Command(CommandKind.UNKNOWN, "unknown", {"text": normalized}, normalized)


def _parse_natural_command(text: str, *, max_text_input_chars: int) -> Command | None:
    if not text:
        return None

    mode = _parse_mode(text)
    if mode is not None:
        return mode

    confirmation = _parse_confirmation(text)
    if confirmation is not None:
        return confirmation

    app = _parse_app(text)
    if app is not None:
        return app

    mouse = _parse_mouse(text)
    if mouse is not None:
        return mouse

    keyboard = _parse_keyboard(text, max_text_input_chars=max_text_input_chars)
    if keyboard is not None:
        return keyboard

    return None


def _has_any(text: str, words: tuple[str, ...]) -> bool:
    return any(word in text for word in words)


def _parse_mode(text: str) -> Command | None:
    if not _has_any(text, ("클로", "claw", "openclaw")):
        return None
    if _has_any(text, ("오프", "꺼", "끄", "중지", "멈춰", "off")):
        return Command(CommandKind.MODE, "set", {"enabled": False}, text)
    if _has_any(text, ("온", "켜", "시작", "on")):
        return Command(CommandKind.MODE, "set", {"enabled": True}, text)
    return None


def _parse_confirmation(text: str) -> Command | None:
    if text in {"응", "예", "네", "확인", "해", "실행", "진행"} or _has_any(text, ("진행해", "실행해", "확인해")):
        return Command(CommandKind.CONFIRMATION, "confirm", raw_text=text)
    if text in {"아니", "아니오", "취소"} or _has_any(text, ("취소해", "하지마", "멈춰")):
        return Command(CommandKind.CONFIRMATION, "cancel", raw_text=text)
    return None


APP_TARGETS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("notepad", ("메모장", "노트패드", "notepad")),
    ("calculator", ("계산기", "calc", "calculator")),
    ("chrome", ("크롬", "브라우저", "chrome")),
    ("explorer", ("파일 탐색기", "탐색기", "explorer")),
)


def _parse_app(text: str) -> Command | None:
    target = None
    for candidate, words in APP_TARGETS:
        if _has_any(text, words):
            target = candidate
            break
    if target is None:
        if _has_any(text, ("창", "윈도우")) and _has_any(text, ("닫", "종료", "꺼")):
            return Command(CommandKind.APP, "close_active_window", {"requires_confirmation": True}, text)
        return None

    if _has_any(text, ("닫", "종료", "꺼", "끄", "나가")):
        return Command(CommandKind.APP, "close", {"target": target, "requires_confirmation": True}, text)
    if _has_any(text, ("열", "켜", "실행", "띄워", "보여")):
        return Command(CommandKind.APP, "open", {"target": target}, text)
    return None


def _parse_mouse(text: str) -> Command | None:
    if "마우스" in text:
        step = "small" if _has_any(text, ("조금", "살짝", "약간")) else "default"
        if "왼쪽 위" in text:
            return Command(CommandKind.MOUSE, "move_position", {"position": "top_left"}, text)
        if "오른쪽 위" in text:
            return Command(CommandKind.MOUSE, "move_position", {"position": "top_right"}, text)
        if "왼쪽 아래" in text:
            return Command(CommandKind.MOUSE, "move_position", {"position": "bottom_left"}, text)
        if "오른쪽 아래" in text:
            return Command(CommandKind.MOUSE, "move_position", {"position": "bottom_right"}, text)
        if _has_any(text, ("가운데", "중앙")):
            return Command(CommandKind.MOUSE, "move_position", {"position": "center"}, text)
        if "왼쪽" in text:
            return Command(CommandKind.MOUSE, "move_relative", {"dx": -1, "dy": 0, "step": step}, text)
        if "오른쪽" in text:
            return Command(CommandKind.MOUSE, "move_relative", {"dx": 1, "dy": 0, "step": step}, text)
        if "위" in text:
            return Command(CommandKind.MOUSE, "move_relative", {"dx": 0, "dy": -1, "step": step}, text)
        if "아래" in text:
            return Command(CommandKind.MOUSE, "move_relative", {"dx": 0, "dy": 1, "step": step}, text)

    if _has_any(text, ("더블 클릭", "두번 클릭", "두 번 클릭")):
        return Command(CommandKind.MOUSE, "double_click", raw_text=text)
    if "클릭" in text and _has_any(text, ("오른쪽", "우클릭")):
        return Command(CommandKind.MOUSE, "click", {"button": "right"}, text)
    if "클릭" in text and _has_any(text, ("왼쪽", "좌클릭", "클릭")):
        return Command(CommandKind.MOUSE, "click", {"button": "left"}, text)
    return None


KEYBOARD_SHORTCUTS: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("복사",), ("ctrl", "c")),
    (("붙여넣", "붙여 넣"), ("ctrl", "v")),
    (("잘라내",), ("ctrl", "x")),
    (("모두 선택", "전체 선택"), ("ctrl", "a")),
    (("실행 취소", "되돌려"), ("ctrl", "z")),
    (("다시 실행", "다시해"), ("ctrl", "y")),
    (("창 전환", "창 바꿔", "알트탭"), ("alt", "tab")),
)


def _parse_keyboard(text: str, *, max_text_input_chars: int) -> Command | None:
    if _has_any(text, ("엔터", "enter")):
        return Command(CommandKind.KEYBOARD, "press", {"key": "enter"}, text)
    if _has_any(text, ("이스케이프", "escape", "esc")):
        return Command(CommandKind.KEYBOARD, "press", {"key": "escape"}, text)

    for words, keys in KEYBOARD_SHORTCUTS:
        if _has_any(text, words):
            return Command(CommandKind.KEYBOARD, "shortcut", {"keys": keys}, text)

    for marker in (" 라고 입력", "라고 입력", " 입력해", " 써줘", " 타이핑"):
        if marker in text:
            text_to_type = text.split(marker, 1)[0].strip()
            if 0 < len(text_to_type) <= max_text_input_chars:
                return Command(CommandKind.KEYBOARD, "type_text", {"text": text_to_type}, text)

    return None
