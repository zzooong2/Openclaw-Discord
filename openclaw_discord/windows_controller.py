from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Protocol, Sequence

from openclaw_discord.commands import Command, CommandKind
from openclaw_discord.filesystem_controller import FolderNavigator


@dataclass(frozen=True)
class AppDefinition:
    start_command: tuple[str, ...]
    process_name: str


APP_COMMANDS: dict[str, AppDefinition] = {
    "notepad": AppDefinition(("notepad.exe",), "notepad.exe"),
    "calculator": AppDefinition(("calc.exe",), "CalculatorApp.exe"),
    "chrome": AppDefinition(("chrome.exe",), "chrome.exe"),
    "explorer": AppDefinition(("explorer.exe",), "explorer.exe"),
}


class ProcessRunner(Protocol):
    def start(self, command: Sequence[str]) -> None:
        """Start a process."""

    def close_app(self, process_name: str) -> None:
        """Close an app by process name."""


class InputDriver(Protocol):
    def move_relative(self, dx: int, dy: int) -> None:
        """Move the mouse relative to its current position."""

    def move_to_position(self, position: str) -> None:
        """Move the mouse to a named screen position."""

    def click(self, button: str) -> None:
        """Click a mouse button."""

    def double_click(self) -> None:
        """Double click the primary mouse button."""

    def press(self, key: str) -> None:
        """Press one key."""

    def shortcut(self, keys: tuple[str, ...]) -> None:
        """Press a keyboard shortcut."""

    def type_text(self, text: str) -> None:
        """Type short text."""


class SubprocessRunner:
    def start(self, command: Sequence[str]) -> None:
        subprocess.Popen(tuple(command))

    def close_app(self, process_name: str) -> None:
        subprocess.run(("taskkill", "/F", "/IM", process_name, "/T"), check=False, capture_output=True)


class PyAutoGuiInputDriver:
    def __init__(
        self,
        *,
        default_step: int = 120,
        small_step: int = 30,
        pyautogui: object | None = None,
        clipboard: object | None = None,
    ) -> None:
        if pyautogui is None:
            import pyautogui

        if clipboard is None:
            import pyperclip as clipboard

        self.pyautogui = pyautogui
        self.clipboard = clipboard
        self.default_step = default_step
        self.small_step = small_step

    def move_relative(self, dx: int, dy: int) -> None:
        self.pyautogui.moveRel(dx, dy)

    def move_to_position(self, position: str) -> None:
        width, height = self.pyautogui.size()
        positions = {
            "center": (width // 2, height // 2),
            "top_left": (0, 0),
            "top_right": (width - 1, 0),
            "bottom_left": (0, height - 1),
            "bottom_right": (width - 1, height - 1),
        }
        self.pyautogui.moveTo(*positions[position])

    def click(self, button: str) -> None:
        self.pyautogui.click(button=button)

    def double_click(self) -> None:
        self.pyautogui.doubleClick()

    def press(self, key: str) -> None:
        self.pyautogui.press(key)

    def shortcut(self, keys: tuple[str, ...]) -> None:
        self.pyautogui.hotkey(*keys)

    def type_text(self, text: str) -> None:
        self.clipboard.copy(text)
        self.pyautogui.hotkey("ctrl", "v")


class WindowsController:
    def __init__(
        self,
        *,
        process_runner: ProcessRunner,
        input_driver: InputDriver,
        folder_navigator: FolderNavigator | None = None,
        default_step: int = 120,
        small_step: int = 30,
    ) -> None:
        self.process_runner = process_runner
        self.input_driver = input_driver
        self.folder_navigator = folder_navigator or FolderNavigator()
        self.default_step = default_step
        self.small_step = small_step

    def execute(self, command: Command) -> str | None:
        if command.kind is CommandKind.APP:
            self._execute_app(command)
        elif command.kind is CommandKind.MOUSE:
            self._execute_mouse(command)
        elif command.kind is CommandKind.KEYBOARD:
            self._execute_keyboard(command)
        elif command.kind is CommandKind.FILESYSTEM:
            return self._execute_filesystem(command)
        else:
            raise ValueError(f"Unsupported command kind: {command.kind.value}")
        return None

    def _execute_app(self, command: Command) -> None:
        if command.action == "close_active_window":
            self.input_driver.shortcut(("alt", "f4"))
            return

        app = APP_COMMANDS[command.payload["target"]]
        if command.action == "open":
            self.process_runner.start(app.start_command)
        elif command.action == "close":
            self.process_runner.close_app(app.process_name)
        else:
            raise ValueError(f"Unsupported app action: {command.action}")

    def _execute_mouse(self, command: Command) -> None:
        if command.action == "move_relative":
            step = self.small_step if command.payload["step"] == "small" else self.default_step
            self.input_driver.move_relative(command.payload["dx"] * step, command.payload["dy"] * step)
        elif command.action == "move_position":
            self.input_driver.move_to_position(command.payload["position"])
        elif command.action == "click":
            self.input_driver.click(command.payload["button"])
        elif command.action == "double_click":
            self.input_driver.double_click()
        else:
            raise ValueError(f"Unsupported mouse action: {command.action}")

    def _execute_keyboard(self, command: Command) -> None:
        if command.action == "press":
            self.input_driver.press(command.payload["key"])
        elif command.action == "shortcut":
            self.input_driver.shortcut(command.payload["keys"])
        elif command.action == "type_text":
            self.input_driver.type_text(command.payload["text"])
        else:
            raise ValueError(f"Unsupported keyboard action: {command.action}")

    def _execute_filesystem(self, command: Command) -> str:
        if command.action == "show_current":
            result = self.folder_navigator.show_current()
        elif command.action == "open_current":
            result = self.folder_navigator.open_current()
        elif command.action == "list_current":
            result = self.folder_navigator.list_current()
        elif command.action == "go_parent":
            result = self.folder_navigator.go_parent()
        elif command.action == "go_to":
            result = self.folder_navigator.go_to(command.payload["target"])
        elif command.action == "open_file":
            result = self.folder_navigator.open_file(command.payload["target"])
        elif command.action == "preview_file":
            result = self.folder_navigator.preview_file(command.payload["target"])
        elif command.action == "close_file":
            result = self.folder_navigator.close_file(command.payload.get("target"))
        else:
            raise ValueError(f"Unsupported filesystem action: {command.action}")

        if not result.ok:
            raise ValueError(result.message)
        if command.action == "close_file":
            self.input_driver.shortcut(("alt", "f4"))
        return result.message
