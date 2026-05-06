from openclaw_discord.commands import parse_command
from openclaw_discord.controllers import RecordedController
from openclaw_discord.core import CommandContext, OpenClawCore
from openclaw_discord.input_blocking import SimulatedInputBlocker


OWNER_ID = "owner-1"


class MemoryLogger:
    def __init__(self):
        self.events = []

    def write(self, event):
        self.events.append(event)


def handle(core: OpenClawCore, text: str, user_id: str = OWNER_ID):
    return core.handle_text(text, CommandContext(user_id=user_id))


def test_rejects_non_owner_commands():
    core = OpenClawCore(owner_user_id=OWNER_ID, controller=RecordedController())

    result = handle(core, "클로 온", user_id="someone-else")

    assert result.ok is False
    assert result.status == "blocked"
    assert result.message == "차단: 허용되지 않은 사용자입니다."
    assert core.voice_mode_enabled is False


def test_turns_voice_mode_on_and_off():
    core = OpenClawCore(owner_user_id=OWNER_ID, controller=RecordedController())

    on_result = handle(core, "클로 온")
    off_result = handle(core, "클로 오프")

    assert on_result.ok is True
    assert on_result.message == "클로 모드가 켜졌습니다."
    assert off_result.ok is True
    assert off_result.message == "클로 모드가 꺼졌습니다."
    assert core.voice_mode_enabled is False


def test_blocks_pc_control_while_mode_is_off():
    controller = RecordedController()
    core = OpenClawCore(owner_user_id=OWNER_ID, controller=controller)

    result = handle(core, "메모장 열어")

    assert result.ok is False
    assert result.status == "blocked"
    assert result.message == "차단: 클로 모드가 꺼져 있습니다."
    assert controller.calls == []


def test_routes_app_command_while_mode_is_on():
    controller = RecordedController()
    core = OpenClawCore(owner_user_id=OWNER_ID, controller=controller)

    handle(core, "클로 온")
    result = handle(core, "메모장 열어")

    assert result.ok is True
    assert result.status == "success"
    assert result.message == "실행 완료: 메모장 열어"
    assert controller.calls == [parse_command("메모장 열어")]


def test_requires_confirmation_for_close_window():
    controller = RecordedController()
    core = OpenClawCore(owner_user_id=OWNER_ID, controller=controller)

    handle(core, "클로 온")
    pending = handle(core, "창 닫아")
    confirmed = handle(core, "확인")

    assert pending.ok is False
    assert pending.status == "pending_confirmation"
    assert pending.message == "확인이 필요합니다: 창 닫아"
    assert confirmed.ok is True
    assert confirmed.message == "실행 완료: 창 닫아"
    assert controller.calls == [parse_command("창 닫아")]


def test_cancel_clears_pending_confirmation():
    controller = RecordedController()
    core = OpenClawCore(owner_user_id=OWNER_ID, controller=controller)

    handle(core, "클로 온")
    handle(core, "창 닫아")
    result = handle(core, "취소")

    assert result.ok is True
    assert result.status == "success"
    assert result.message == "대기 중인 명령을 취소했습니다."
    assert controller.calls == []


def test_logs_voice_command_and_result():
    logger = MemoryLogger()
    core = OpenClawCore(owner_user_id=OWNER_ID, controller=RecordedController(), logger=logger)

    handle(core, "클로 온")

    assert [event.type for event in logger.events] == ["voice_command", "success"]
    assert logger.events[0].message == "클로 온"
    assert logger.events[1].message == "클로 모드가 켜졌습니다."


def test_mode_on_and_off_controls_input_blocker():
    blocker = SimulatedInputBlocker()
    core = OpenClawCore(owner_user_id=OWNER_ID, controller=RecordedController(), input_blocker=blocker)

    handle(core, "클로 온")
    assert blocker.enabled is True

    handle(core, "클로 오프")
    assert blocker.enabled is False
