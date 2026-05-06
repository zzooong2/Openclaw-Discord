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

    assert command.kind is CommandKind.APP
    assert command.action == "open"
    assert command.payload == {"target": "chrome"}


def test_understands_natural_mode_on_request():
    command = parse_command("클로 모드 켜줘")

    assert command.kind is CommandKind.MODE
    assert command.action == "set"
    assert command.payload == {"enabled": True}


def test_understands_natural_app_close_request():
    command = parse_command("계산기 좀 종료해줘")

    assert command.kind is CommandKind.APP
    assert command.action == "close"
    assert command.payload == {"target": "calculator"}


def test_exact_app_close_command_does_not_require_confirmation():
    command = parse_command("계산기 닫아")

    assert command.kind is CommandKind.APP
    assert command.action == "close"
    assert command.payload == {"target": "calculator"}


def test_understands_natural_mouse_move_request():
    command = parse_command("마우스 살짝 왼쪽으로 옮겨")

    assert command.kind is CommandKind.MOUSE
    assert command.action == "move_relative"
    assert command.payload == {"dx": -1, "dy": 0, "step": "small"}


def test_understands_natural_text_input_request():
    command = parse_command("안녕하세요 라고 입력해줘")

    assert command.kind is CommandKind.KEYBOARD
    assert command.action == "type_text"
    assert command.payload == {"text": "안녕하세요"}


def test_parses_show_current_folder_request():
    command = parse_command("현재 폴더 보여줘")

    assert command.kind is CommandKind.FILESYSTEM
    assert command.action == "show_current"


def test_parses_open_current_folder_request():
    command = parse_command("폴더 열어")

    assert command.kind is CommandKind.FILESYSTEM
    assert command.action == "open_current"


def test_parses_go_parent_folder_request():
    command = parse_command("상위 폴더로 가")

    assert command.kind is CommandKind.FILESYSTEM
    assert command.action == "go_parent"


def test_parses_go_to_named_folder_request():
    command = parse_command("다운로드 폴더로 들어가")

    assert command.kind is CommandKind.FILESYSTEM
    assert command.action == "go_to"
    assert command.payload == {"target": "Downloads"}


def test_parses_go_to_searches_folder_request():
    command = parse_command("검색 폴더로 가줘")

    assert command.kind is CommandKind.FILESYSTEM
    assert command.action == "go_to"
    assert command.payload == {"target": "Searches"}


def test_rejects_unknown_natural_request():
    command = parse_command("오늘 날씨 알려줘")

    assert command.kind is CommandKind.UNKNOWN
    assert command.action == "unknown"
    assert command.payload == {"text": "오늘 날씨 알려줘"}


def test_rejects_empty_text_input():
    command = parse_command("입력")

    assert command.kind is CommandKind.UNKNOWN
    assert command.action == "unknown"
