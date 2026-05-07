from pathlib import Path

from openclaw_discord.filesystem_controller import FolderNavigator, ReusingWindowsFolderRunner


class FakeFolderRunner:
    def __init__(self):
        self.opened = []

    def open_folder(self, path):
        self.opened.append(path)


def test_folder_navigator_shows_current_folder(tmp_path):
    navigator = FolderNavigator(current_path=tmp_path, runner=FakeFolderRunner())

    result = navigator.show_current()

    assert result.ok is True
    assert result.message == f"현재 폴더: {tmp_path.resolve()}"


def test_folder_navigator_opens_current_folder(tmp_path):
    runner = FakeFolderRunner()
    navigator = FolderNavigator(current_path=tmp_path, runner=runner)

    result = navigator.open_current()

    assert result.ok is True
    assert runner.opened == [tmp_path.resolve()]


def test_folder_navigator_goes_to_child_folder(tmp_path):
    child = tmp_path / "work"
    child.mkdir()
    runner = FakeFolderRunner()
    navigator = FolderNavigator(current_path=tmp_path, runner=runner)

    result = navigator.go_to("work")

    assert result.ok is True
    assert navigator.current_path == child.resolve()
    assert runner.opened == [child.resolve()]


def test_folder_navigator_goes_to_child_folder_by_display_name(tmp_path):
    child = tmp_path / "검색 결과"
    child.mkdir()
    runner = FakeFolderRunner()
    navigator = FolderNavigator(current_path=tmp_path, runner=runner)

    result = navigator.go_to("검색")

    assert result.ok is True
    assert navigator.current_path == child.resolve()
    assert runner.opened == [child.resolve()]


def test_folder_navigator_goes_to_child_folder_ignoring_case_and_spaces(tmp_path):
    child = tmp_path / "OpenClaw Discord"
    child.mkdir()
    runner = FakeFolderRunner()
    navigator = FolderNavigator(current_path=tmp_path, runner=runner)

    result = navigator.go_to("openclawdiscord")

    assert result.ok is True
    assert navigator.current_path == child.resolve()
    assert runner.opened == [child.resolve()]


def test_folder_navigator_goes_to_folder_from_extra_search_root(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    drive_root = tmp_path / "drive"
    drive_root.mkdir()
    project = drive_root / "project"
    project.mkdir()
    runner = FakeFolderRunner()
    navigator = FolderNavigator(current_path=home, extra_search_roots=[drive_root], runner=runner)

    result = navigator.go_to("project")

    assert result.ok is True
    assert navigator.current_path == project.resolve()
    assert runner.opened == [project.resolve()]


def test_folder_navigator_goes_to_parent_folder(tmp_path):
    child = tmp_path / "work"
    child.mkdir()
    runner = FakeFolderRunner()
    navigator = FolderNavigator(current_path=child, runner=runner)

    result = navigator.go_parent()

    assert result.ok is True
    assert navigator.current_path == tmp_path.resolve()
    assert runner.opened == [tmp_path.resolve()]


def test_reusing_windows_folder_runner_reuses_existing_explorer_window(tmp_path):
    shell = FakeShell([FakeExplorerWindow()])
    runner = ReusingWindowsFolderRunner(shell_factory=lambda: shell, fallback_runner=FakeFolderRunner())

    runner.open_folder(tmp_path)

    assert shell.windows[0].navigated == [str(tmp_path.resolve())]


def test_reusing_windows_folder_runner_falls_back_when_no_explorer_window(tmp_path):
    fallback = FakeFolderRunner()
    runner = ReusingWindowsFolderRunner(shell_factory=lambda: FakeShell([]), fallback_runner=fallback)

    runner.open_folder(tmp_path)

    assert fallback.opened == [tmp_path.resolve()]


def test_reusing_windows_folder_runner_falls_back_when_navigation_fails(tmp_path):
    fallback = FakeFolderRunner()
    shell = FakeShell([FakeExplorerWindow(navigate_error=RuntimeError("boom"))])
    runner = ReusingWindowsFolderRunner(shell_factory=lambda: shell, fallback_runner=fallback)

    runner.open_folder(tmp_path)

    assert fallback.opened == [tmp_path.resolve()]


def test_folder_navigator_rejects_missing_folder(tmp_path):
    navigator = FolderNavigator(current_path=tmp_path, runner=FakeFolderRunner())

    result = navigator.go_to("missing")

    assert result.ok is False
    assert result.message == f"폴더를 찾을 수 없습니다: {(tmp_path / 'missing').resolve()}"
    assert navigator.current_path == tmp_path.resolve()


def test_folder_navigator_reports_ambiguous_child_folder_match(tmp_path):
    (tmp_path / "검색 A").mkdir()
    (tmp_path / "검색 B").mkdir()
    navigator = FolderNavigator(current_path=tmp_path, runner=FakeFolderRunner())

    result = navigator.go_to("검색")

    assert result.ok is False
    assert result.message == "폴더 이름이 여러 개와 일치합니다: 검색 A, 검색 B"
    assert navigator.current_path == tmp_path.resolve()


def test_folder_navigator_rejects_paths_outside_sandbox(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    navigator = FolderNavigator(current_path=root, sandbox_root=root, runner=FakeFolderRunner())

    result = navigator.go_to(outside)

    assert result.ok is False
    assert result.message == f"허용된 루트 밖입니다: {outside.resolve()}"
    assert navigator.current_path == root.resolve()


def test_folder_navigator_starts_at_sandbox_root_when_current_path_is_omitted(tmp_path):
    root = tmp_path / "root"
    root.mkdir()

    navigator = FolderNavigator(sandbox_root=root, runner=FakeFolderRunner())

    assert navigator.current_path == root.resolve()


def test_folder_navigator_does_not_search_extra_roots_outside_sandbox(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "project").mkdir()
    navigator = FolderNavigator(sandbox_root=root, extra_search_roots=[outside], runner=FakeFolderRunner())

    result = navigator.go_to("project")

    assert result.ok is False
    assert result.message == f"폴더를 찾을 수 없습니다: {(root / 'project').resolve()}"
    assert navigator.current_path == root.resolve()


class FakeLocation:
    def __init__(self, url="file:///C:/Users"):
        self.URL = url


class FakeExplorerWindow:
    def __init__(self, *, navigate_error=None):
        self.LocationURL = "file:///C:/Users"
        self.Document = type("Document", (), {"Folder": type("Folder", (), {"Self": FakeLocation()})()})()
        self.navigated = []
        self.navigate_error = navigate_error

    def Navigate(self, url):
        if self.navigate_error is not None:
            raise self.navigate_error
        self.navigated.append(url)


class FakeShell:
    def __init__(self, windows):
        self.windows = windows

    def Windows(self):
        return self.windows
