from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol


class FolderRunner(Protocol):
    def open_folder(self, path: Path) -> None:
        """Open a folder in the platform file manager."""

    def open_file(self, path: Path) -> None:
        """Open a file with its default application."""


class WindowsFolderRunner:
    def open_folder(self, path: Path) -> None:
        os.startfile(str(path))  # type: ignore[attr-defined]

    def open_file(self, path: Path) -> None:
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

        try:
            window.Navigate(str(resolved))
        except Exception:
            self.fallback_runner.open_folder(resolved)

    def open_file(self, path: Path) -> None:
        self.fallback_runner.open_file(path.resolve())

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
    candidates: list[Path] | None = None


class FolderNavigator:
    def __init__(
        self,
        *,
        current_path: Path | None = None,
        sandbox_root: Path | None = None,
        extra_search_roots: list[Path] | None = None,
        runner: FolderRunner | None = None,
    ) -> None:
        self.sandbox_root = sandbox_root.resolve() if sandbox_root is not None else None
        self.current_path = self._initial_current_path(current_path)
        self.extra_search_roots = self._allowed_search_roots(extra_search_roots)
        self.runner = runner or ReusingWindowsFolderRunner()

    def show_current(self) -> FolderActionResult:
        return FolderActionResult(True, f"현재 폴더: {self.current_path}", self.current_path)

    def open_current(self) -> FolderActionResult:
        self.runner.open_folder(self.current_path)
        return FolderActionResult(True, f"폴더를 열었습니다: {self.current_path}", self.current_path)

    def list_current(self) -> FolderActionResult:
        try:
            children = sorted(self.current_path.iterdir(), key=lambda child: (not child.is_dir(), child.name.casefold()))
        except OSError as exc:
            return FolderActionResult(False, f"목록을 읽을 수 없습니다: {exc}", self.current_path)

        lines = [f"현재 폴더: {self.current_path}"]
        if not children:
            lines.append("(비어 있음)")
        for child in children[:30]:
            label = "폴더" if child.is_dir() else "파일"
            lines.append(f"[{label}] {child.name}")
        if len(children) > 30:
            lines.append(f"... 외 {len(children) - 30}개")
        return FolderActionResult(True, "\n".join(lines), self.current_path)

    def open_file(self, target: str | Path) -> FolderActionResult:
        result = self._resolve_file(target)
        if not result.ok:
            return result
        self.runner.open_file(result.path)
        return FolderActionResult(True, f"파일을 열었습니다: {result.path}", result.path)

    def preview_file(self, target: str | Path, *, max_chars: int = 1300) -> FolderActionResult:
        result = self._resolve_file(target)
        if not result.ok:
            return result
        path = result.path
        try:
            data = path.read_bytes()
        except OSError as exc:
            return FolderActionResult(False, f"파일을 읽을 수 없습니다: {exc}", self.current_path)
        if b"\x00" in data[:1024]:
            return FolderActionResult(False, f"텍스트 파일로 보기 어렵습니다: {path}", path)
        text = data.decode("utf-8-sig", errors="replace")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        truncated = text[:max_chars]
        if len(text) > max_chars:
            truncated += "\n..."
        return FolderActionResult(True, f"파일 미리보기: {path}\n```text\n{truncated}\n```", path)

    def close_file(self, target: str | Path | None = None) -> FolderActionResult:
        if target is None:
            return FolderActionResult(True, "파일 창을 닫았습니다.", self.current_path)
        result = self._resolve_file(target)
        if not result.ok:
            return result
        return FolderActionResult(True, "파일 창을 닫았습니다.", result.path)

    def go_parent(self) -> FolderActionResult:
        return self.go_to(self.current_path.parent)

    def go_to(self, target: str | Path) -> FolderActionResult:
        path = self._resolve_target(target)
        matched_children: list[Path] | None = None
        if not path.exists() and isinstance(target, str):
            matched_children = self._find_child_folder_matches(target)
            if len(matched_children) == 1:
                path = matched_children[0]
            elif len(matched_children) > 1:
                names = ", ".join(child.name for child in matched_children[:5])
                return FolderActionResult(
                    False,
                    f"폴더 이름이 여러 개와 일치합니다: {names}",
                    self.current_path,
                    matched_children,
                )
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

        for root in self.extra_search_roots:
            candidate = root / path
            if candidate.exists():
                return self._normalize(candidate)

        return self._normalize(self.current_path / path)

    def _resolve_file(self, target: str | Path) -> FolderActionResult:
        path = self._resolve_target(target)
        matched_files: list[Path] | None = None
        if not path.exists() and isinstance(target, str):
            matched_files = self._find_child_file_matches(target)
            if len(matched_files) == 1:
                path = matched_files[0]
            elif len(matched_files) > 1:
                names = ", ".join(child.name for child in matched_files[:5])
                return FolderActionResult(False, f"파일 이름이 여러 개와 일치합니다: {names}", self.current_path, matched_files)
        if not path.exists():
            return FolderActionResult(False, f"파일을 찾을 수 없습니다: {path}", self.current_path)
        if not path.is_file():
            return FolderActionResult(False, f"파일이 아닙니다: {path}", self.current_path)
        if not self._is_allowed(path):
            return FolderActionResult(False, f"허용된 루트 밖입니다: {path}", self.current_path)
        return FolderActionResult(True, "", path.resolve())

    def _normalize(self, path: Path) -> Path:
        return path.expanduser().resolve()

    def _initial_current_path(self, current_path: Path | None) -> Path:
        if current_path is not None:
            normalized = self._normalize(current_path)
            if self._is_allowed(normalized):
                return normalized
        if self.sandbox_root is not None:
            return self.sandbox_root
        return self._normalize(Path.home())

    def _allowed_search_roots(self, extra_search_roots: list[Path] | None) -> list[Path]:
        if self.sandbox_root is not None:
            roots = [self.sandbox_root]
            for root in extra_search_roots or []:
                normalized = self._normalize(root)
                if self._is_allowed(normalized) and normalized not in roots:
                    roots.append(normalized)
            return roots

        return [self._normalize(root) for root in extra_search_roots or self._default_extra_search_roots()]

    def _is_allowed(self, path: Path) -> bool:
        if self.sandbox_root is None:
            return True
        try:
            path.resolve().relative_to(self.sandbox_root)
        except ValueError:
            return False
        return True

    def _find_child_folder_matches(self, target: str) -> list[Path]:
        target_key = self._match_key(target)
        if not target_key:
            return []

        try:
            children = [
                child
                for root in self._search_roots()
                for child in self._safe_child_directories(root)
                if self._is_allowed(child)
            ]
        except OSError:
            return []

        exact = [child for child in children if self._match_key(child.name) == target_key]
        if exact:
            return sorted(exact, key=lambda child: child.name.lower())

        contained = [
            child
            for child in children
            if target_key in self._match_key(child.name)
        ]
        return sorted(contained, key=lambda child: child.name.lower())

    def _find_child_file_matches(self, target: str) -> list[Path]:
        target_key = self._match_key(target)
        if not target_key:
            return []
        try:
            children = [child for child in self.current_path.iterdir() if child.is_file() and self._is_allowed(child)]
        except OSError:
            return []

        exact = [child for child in children if self._match_key(child.name) == target_key or self._match_key(child.stem) == target_key]
        if exact:
            return sorted(exact, key=lambda child: child.name.lower())

        contained = [
            child
            for child in children
            if target_key in self._match_key(child.name) or target_key in self._match_key(child.stem)
        ]
        return sorted(contained, key=lambda child: child.name.lower())

    @staticmethod
    def _match_key(value: str) -> str:
        return "".join(character for character in value.casefold() if character.isalnum())

    def _search_roots(self) -> list[Path]:
        roots = [self.current_path]
        for root in self.extra_search_roots:
            if root not in roots:
                roots.append(root)
        return roots

    @staticmethod
    def _safe_child_directories(root: Path) -> list[Path]:
        try:
            return [child for child in root.iterdir() if child.is_dir()]
        except OSError:
            return []

    @staticmethod
    def _default_extra_search_roots() -> list[Path]:
        roots = [Path("C:/")]
        return [root for root in roots if root.exists()]
