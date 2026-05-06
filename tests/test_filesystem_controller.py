from pathlib import Path

from openclaw_discord.filesystem_controller import FolderNavigator


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


def test_folder_navigator_goes_to_parent_folder(tmp_path):
    child = tmp_path / "work"
    child.mkdir()
    runner = FakeFolderRunner()
    navigator = FolderNavigator(current_path=child, runner=runner)

    result = navigator.go_parent()

    assert result.ok is True
    assert navigator.current_path == tmp_path.resolve()
    assert runner.opened == [tmp_path.resolve()]


def test_folder_navigator_rejects_missing_folder(tmp_path):
    navigator = FolderNavigator(current_path=tmp_path, runner=FakeFolderRunner())

    result = navigator.go_to("missing")

    assert result.ok is False
    assert result.message == f"폴더를 찾을 수 없습니다: {(tmp_path / 'missing').resolve()}"
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
