from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol


class FolderRunner(Protocol):
    def open_folder(self, path: Path) -> None:
        """Open a folder in the platform file manager."""


class WindowsFolderRunner:
    def open_folder(self, path: Path) -> None:
        os.startfile(str(path))  # type: ignore[attr-defined]


class ReusingWindowsFolderRunner:
    def __init__(
        self,
        *,
        shell_factory: Callable[[], object] | None = None,
        fallback_runner: FolderRunner | None = None,
    ) -> None:
        self.shell_factory = shell_factory or self._create_shell
        self.fallback_runner = fallback_runner or WindowsFolderRunner()

    def open_folder(self, path: Path) -> None:
        resolved = path.resolve()
        window = self._find_explorer_window()
        if window is None:
            self.fallback_runner.open_folder(resolved)
            return

        window.Navigate(resolved.as_uri())

    def _find_explorer_window(self) -> object | None:
        try:
            shell = self.shell_factory()
            windows = shell.Windows()
        except Exception:
            return None

        for window in windows:
            if self._is_explorer_window(window):
                return window
        return None

    @staticmethod
    def _is_explorer_window(window: object) -> bool:
        location_url = str(getattr(window, "LocationURL", ""))
        if location_url.startswith("file:"):
            return True
        try:
            folder_url = str(window.Document.Folder.Self.URL)
        except Exception:
            return False
        return folder_url.startswith("file:")

    @staticmethod
    def _create_shell() -> object:
        import win32com.client

        return win32com.client.Dispatch("Shell.Application")


@dataclass
class FolderActionResult:
    ok: bool
    message: str
    path: Path


class FolderNavigator:
    def __init__(
        self,
        *,
        current_path: Path | None = None,
        sandbox_root: Path | None = None,
        runner: FolderRunner | None = None,
    ) -> None:
        self.sandbox_root = sandbox_root.resolve() if sandbox_root is not None else None
        self.current_path = self._normalize(current_path or Path.home())
        self.runner = runner or ReusingWindowsFolderRunner()

    def show_current(self) -> FolderActionResult:
        return FolderActionResult(True, f"현재 폴더: {self.current_path}", self.current_path)

    def open_current(self) -> FolderActionResult:
        self.runner.open_folder(self.current_path)
        return FolderActionResult(True, f"폴더를 열었습니다: {self.current_path}", self.current_path)

    def go_parent(self) -> FolderActionResult:
        return self.go_to(self.current_path.parent)

    def go_to(self, target: str | Path) -> FolderActionResult:
        path = self._resolve_target(target)
        if not path.exists():
            return FolderActionResult(False, f"폴더를 찾을 수 없습니다: {path}", self.current_path)
        if not path.is_dir():
            return FolderActionResult(False, f"폴더가 아닙니다: {path}", self.current_path)
        if not self._is_allowed(path):
            return FolderActionResult(False, f"허용된 루트 밖입니다: {path}", self.current_path)

        self.current_path = path.resolve()
        self.runner.open_folder(self.current_path)
        return FolderActionResult(True, f"이동한 폴더: {self.current_path}", self.current_path)

    def _resolve_target(self, target: str | Path) -> Path:
        path = Path(target)
        if path.is_absolute():
            return self._normalize(path)

        home_candidate = Path.home() / path
        if home_candidate.exists():
            return self._normalize(home_candidate)

        return self._normalize(self.current_path / path)

    def _normalize(self, path: Path) -> Path:
        return path.expanduser().resolve()

    def _is_allowed(self, path: Path) -> bool:
        if self.sandbox_root is None:
            return True
        try:
            path.resolve().relative_to(self.sandbox_root)
        except ValueError:
            return False
        return True
