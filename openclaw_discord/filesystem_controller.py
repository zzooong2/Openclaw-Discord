from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence


class FolderRunner(Protocol):
    def open_folder(self, path: Path) -> None:
        """Open a folder in the platform file manager."""


class WindowsFolderRunner:
    def open_folder(self, path: Path) -> None:
        os.startfile(str(path))  # type: ignore[attr-defined]


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
        self.runner = runner or WindowsFolderRunner()

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
