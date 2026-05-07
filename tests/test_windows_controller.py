from openclaw_discord.commands import parse_command
from openclaw_discord.windows_controller import (
    APP_COMMANDS,
    PyAutoGuiInputDriver,
    SubprocessRunner,
    WindowsController,
)


class FakeProcessRunner:
    def __init__(self):
        self.started = []
        self.closed = []

    def start(self, command):
        self.started.append(command)

    def close_app(self, process_name):
        self.closed.append(process_name)


class FakeInputDriver:
    def __init__(self):
        self.calls = []

    def move_relative(self, dx, dy):
        self.calls.append(("move_relative", dx, dy))

    def move_to_position(self, position):
        self.calls.append(("move_to_position", position))

    def click(self, button):
        self.calls.append(("click", button))

    def double_click(self):
        self.calls.append(("double_click",))

    def press(self, key):
        self.calls.append(("press", key))

    def shortcut(self, keys):
        self.calls.append(("shortcut", keys))

    def type_text(self, text):
        self.calls.append(("type_text", text))


class FakeFolderNavigator:
    def __init__(self):
        self.calls = []

    def show_current(self):
        self.calls.append(("show_current",))
        return type("Result", (), {"ok": True, "message": "현재 폴더: C:\\work"})()

    def open_current(self):
        self.calls.append(("open_current",))
        return type("Result", (), {"ok": True, "message": "폴더를 열었습니다: C:\\work"})()

    def list_current(self):
        self.calls.append(("list_current",))
        return type("Result", (), {"ok": True, "message": "현재 폴더: C:\\work\n[파일] README.md"})()

    def go_parent(self):
        self.calls.append(("go_parent",))
        return type("Result", (), {"ok": True, "message": "이동한 폴더: C:\\"})()

    def go_to(self, target):
        self.calls.append(("go_to", target))
        return type("Result", (), {"ok": True, "message": f"이동한 폴더: {target}"})()

    def open_file(self, target):
        self.calls.append(("open_file", target))
        return type("Result", (), {"ok": True, "message": f"파일을 열었습니다: {target}"})()

    def preview_file(self, target):
        self.calls.append(("preview_file", target))
        return type("Result", (), {"ok": True, "message": f"파일 미리보기: {target}"})()


class FakePyAutoGui:
    def __init__(self):
        self.calls = []

    def hotkey(self, *keys):
        self.calls.append(("hotkey", keys))


class FakeClipboard:
    def __init__(self):
        self.copied = []

    def copy(self, text):
        self.copied.append(text)


def test_opens_known_app():
    runner = FakeProcessRunner()
    controller = WindowsController(process_runner=runner, input_driver=FakeInputDriver())

    controller.execute(parse_command("메모장 열어"))

    assert runner.started == [APP_COMMANDS["notepad"].start_command]


def test_closes_known_app():
    runner = FakeProcessRunner()
    controller = WindowsController(process_runner=runner, input_driver=FakeInputDriver())

    controller.execute(parse_command("메모장 닫아"))

    assert runner.closed == [APP_COMMANDS["notepad"].process_name]


def test_subprocess_runner_force_closes_app(monkeypatch):
    calls = []

    def fake_run(command, *, check, capture_output):
        calls.append((command, check, capture_output))

    monkeypatch.setattr("openclaw_discord.windows_controller.subprocess.run", fake_run)

    SubprocessRunner().close_app("CalculatorApp.exe")

    assert calls == [(("taskkill", "/F", "/IM", "CalculatorApp.exe", "/T"), False, True)]


def test_moves_mouse_by_default_step():
    input_driver = FakeInputDriver()
    controller = WindowsController(process_runner=FakeProcessRunner(), input_driver=input_driver)

    controller.execute(parse_command("마우스 오른쪽으로"))

    assert input_driver.calls == [("move_relative", 120, 0)]


def test_moves_mouse_by_small_step():
    input_driver = FakeInputDriver()
    controller = WindowsController(process_runner=FakeProcessRunner(), input_driver=input_driver)

    controller.execute(parse_command("마우스 조금 위로"))

    assert input_driver.calls == [("move_relative", 0, -30)]


def test_moves_mouse_to_named_position():
    input_driver = FakeInputDriver()
    controller = WindowsController(process_runner=FakeProcessRunner(), input_driver=input_driver)

    controller.execute(parse_command("마우스 가운데로"))

    assert input_driver.calls == [("move_to_position", "center")]


def test_sends_click_and_keyboard_commands():
    input_driver = FakeInputDriver()
    controller = WindowsController(process_runner=FakeProcessRunner(), input_driver=input_driver)

    controller.execute(parse_command("왼쪽 클릭"))
    controller.execute(parse_command("더블 클릭"))
    controller.execute(parse_command("복사"))
    controller.execute(parse_command("안녕하세요 입력"))

    assert input_driver.calls == [
        ("click", "left"),
        ("double_click",),
        ("shortcut", ("ctrl", "c")),
        ("type_text", "안녕하세요"),
    ]


def test_pyautogui_input_driver_types_text_through_clipboard_paste():
    pyautogui = FakePyAutoGui()
    clipboard = FakeClipboard()
    driver = PyAutoGuiInputDriver(pyautogui=pyautogui, clipboard=clipboard)

    driver.type_text("안녕하세요")

    assert clipboard.copied == ["안녕하세요"]
    assert pyautogui.calls == [("hotkey", ("ctrl", "v"))]


def test_executes_filesystem_command_and_returns_message():
    folder_navigator = FakeFolderNavigator()
    controller = WindowsController(
        process_runner=FakeProcessRunner(),
        input_driver=FakeInputDriver(),
        folder_navigator=folder_navigator,
    )

    message = controller.execute(parse_command("다운로드 폴더로 들어가"))

    assert message == "이동한 폴더: Downloads"
    assert folder_navigator.calls == [("go_to", "Downloads")]


def test_executes_filesystem_file_commands_and_returns_message():
    folder_navigator = FakeFolderNavigator()
    controller = WindowsController(
        process_runner=FakeProcessRunner(),
        input_driver=FakeInputDriver(),
        folder_navigator=folder_navigator,
    )

    list_message = controller.execute(parse_command("목록 보여줘"))
    open_message = controller.execute(parse_command("README.md 파일 열어줘"))
    preview_message = controller.execute(parse_command("README.md 파일 내용 일부 보여줘"))

    assert list_message == "현재 폴더: C:\\work\n[파일] README.md"
    assert open_message == "파일을 열었습니다: README.md"
    assert preview_message == "파일 미리보기: README.md"
