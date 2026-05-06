from openclaw_discord.commands import CommandKind, parse_command


def test_parses_mode_on_command():
    command = parse_command("클로 온")

    assert command.kind is CommandKind.MODE
    assert command.action == "set"
    assert command.payload == {"enabled": True}


def test_parses_mode_off_command():
    command = parse_command("클로 오프")

    assert command.kind is CommandKind.MODE
    assert command.action == "set"
    assert command.payload == {"enabled": False}


def test_parses_app_open_command():
    command = parse_command("메모장 열어")

    assert command.kind is CommandKind.APP
    assert command.action == "open"
    assert command.payload == {"target": "notepad"}


def test_parses_mouse_click_command():
    command = parse_command("왼쪽 클릭")

    assert command.kind is CommandKind.MOUSE
    assert command.action == "click"
    assert command.payload == {"button": "left"}


def test_parses_keyboard_shortcut_command():
    command = parse_command("복사")

    assert command.kind is CommandKind.KEYBOARD
    assert command.action == "shortcut"
    assert command.payload == {"keys": ("ctrl", "c")}


def test_parses_short_text_input_command():
    command = parse_command("안녕하세요 입력")

    assert command.kind is CommandKind.KEYBOARD
    assert command.action == "type_text"
    assert command.payload == {"text": "안녕하세요"}


def test_rejects_unknown_command():
    command = parse_command("브라우저 좀 켜줘")

    assert command.kind is CommandKind.UNKNOWN
    assert command.action == "unknown"
    assert command.payload == {"text": "브라우저 좀 켜줘"}


def test_rejects_empty_text_input():
    command = parse_command("입력")

    assert command.kind is CommandKind.UNKNOWN
    assert command.action == "unknown"

