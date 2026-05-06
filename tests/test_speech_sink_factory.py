from openclaw_discord.speech_sink_factory import SpeechRecognitionSinkFactory


class FakeUser:
    id = 123


class FakeBridge:
    def __init__(self):
        self.submissions = []

    def submit(self, text, *, user_id):
        self.submissions.append((text, user_id))


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

