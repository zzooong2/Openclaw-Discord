from openclaw_discord.speech_recognizer import ExactPhraseRecognizer


def test_exact_phrase_recognizer_returns_allowed_phrase():
    recognizer = ExactPhraseRecognizer({"클로 온", "클로 오프"})

    assert recognizer.recognize(" 클로   온 ") == "클로 온"


def test_exact_phrase_recognizer_rejects_unknown_phrase():
    recognizer = ExactPhraseRecognizer({"클로 온"})

    assert recognizer.recognize("크롬 켜줘") is None

