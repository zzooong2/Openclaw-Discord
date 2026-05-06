import asyncio

from openclaw_discord.speech_bridge import ThreadSafeSpeechBridge


class FakePipeline:
    def __init__(self):
        self.calls = []

    async def process_recognized_text(self, text, *, user_id):
        self.calls.append((text, user_id))


def test_bridge_schedules_recognized_text_on_event_loop():
    async def scenario():
        pipeline = FakePipeline()
        bridge = ThreadSafeSpeechBridge(loop=asyncio.get_running_loop(), pipeline=pipeline)

        future = bridge.submit("클로 온", user_id="owner-1")
        await asyncio.wrap_future(future)

        assert pipeline.calls == [("클로 온", "owner-1")]

    asyncio.run(scenario())


def test_bridge_ignores_blank_text():
    async def scenario():
        pipeline = FakePipeline()
        bridge = ThreadSafeSpeechBridge(loop=asyncio.get_running_loop(), pipeline=pipeline)

        future = bridge.submit("   ", user_id="owner-1")

        assert future is None
        assert pipeline.calls == []

    asyncio.run(scenario())

