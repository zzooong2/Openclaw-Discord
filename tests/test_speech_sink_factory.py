import asyncio

from openclaw_discord.speech_sink_factory import SpeechRecognitionSinkFactory


class FakeUser:
    id = 123


class FakeBridge:
    def __init__(self, loop=None):
        self.submissions = []
        self.loop = loop

    def submit(self, text, *, user_id):
        self.submissions.append((text, user_id))


class FakeNotifier:
    def __init__(self):
        self.messages = []

    async def send(self, message):
        self.messages.append(message)


class FakeSpeechRecognitionSink:
    def __init__(self, *, text_cb, default_recognizer, phrase_time_limit):
        self.text_cb = text_cb
        self.default_recognizer = default_recognizer
        self.phrase_time_limit = phrase_time_limit


class FakeSpeechRecognitionModule:
    SpeechRecognitionSink = FakeSpeechRecognitionSink


def test_factory_creates_sink_that_submits_recognized_text_to_bridge():
    bridge = FakeBridge()
    factory = SpeechRecognitionSinkFactory(
        bridge=bridge,
        speech_recognition_module=FakeSpeechRecognitionModule,
        recognizer_name="google",
        phrase_time_limit=3,
    )

    sink = factory.create()
    sink.text_cb(FakeUser(), "클로 온")

    assert sink.default_recognizer == "google"
    assert sink.phrase_time_limit == 3
    assert bridge.submissions == [("클로 온", "123")]


def test_factory_notifies_recognized_text_when_notifier_is_configured():
    async def scenario():
        bridge = FakeBridge(loop=asyncio.get_running_loop())
        notifier = FakeNotifier()
        factory = SpeechRecognitionSinkFactory(
            bridge=bridge,
            text_notifier=notifier,
            speech_recognition_module=FakeSpeechRecognitionModule,
        )

        sink = factory.create()
        sink.text_cb(FakeUser(), "클로 온")
        await asyncio.sleep(0.01)

        assert notifier.messages == ["음성 인식: 클로 온"]

    asyncio.run(scenario())
