from openclaw_discord.commands import parse_command
from openclaw_discord.windows_controller import (
    APP_COMMANDS,
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

