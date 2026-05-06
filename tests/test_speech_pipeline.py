import asyncio

from openclaw_discord.controllers import RecordedController
from openclaw_discord.core import OpenClawCore
from openclaw_discord.input_blocking import SimulatedInputBlocker
from openclaw_discord.speech_pipeline import SpeechCommandPipeline


OWNER_ID = "owner-1"


class MemoryNotifier:
    def __init__(self):
        self.messages = []

    async def send(self, message):
        self.messages.append(message)


def build_pipeline():
    controller = RecordedController()
    blocker = SimulatedInputBlocker()
    core = OpenClawCore(owner_user_id=OWNER_ID, controller=controller, input_blocker=blocker)
    notifier = MemoryNotifier()
    pipeline = SpeechCommandPipeline(core=core, text_notifier=notifier)
    return pipeline, core, controller, blocker, notifier


def test_processes_owner_speech_text_through_core():
    pipeline, core, _, blocker, notifier = build_pipeline()

    result = asyncio.run(pipeline.process_recognized_text("클로 온", user_id=OWNER_ID))

    assert result.ok is True
    assert result.message == "클로 모드가 켜졌습니다."
    assert core.voice_mode_enabled is True
    assert blocker.enabled is True
    assert notifier.messages == ["클로 모드가 켜졌습니다."]


def test_blocks_non_owner_speech_text():
    pipeline, core, _, blocker, notifier = build_pipeline()

    result = asyncio.run(pipeline.process_recognized_text("클로 온", user_id="someone-else"))

    assert result.ok is False
    assert result.message == "차단: 허용되지 않은 사용자입니다."
    assert core.voice_mode_enabled is False
    assert blocker.enabled is False
    assert notifier.messages == ["차단: 허용되지 않은 사용자입니다."]


def test_processes_pc_command_after_mode_on():
    pipeline, _, controller, _, notifier = build_pipeline()

    asyncio.run(pipeline.process_recognized_text("클로 온", user_id=OWNER_ID))
    result = asyncio.run(pipeline.process_recognized_text("메모장 열어", user_id=OWNER_ID))

    assert result.ok is True
    assert result.message == "실행 완료: 메모장 열어"
    assert len(controller.calls) == 1
    assert notifier.messages[-1] == "실행 완료: 메모장 열어"

