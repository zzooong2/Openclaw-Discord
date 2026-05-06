import asyncio
import json

from openclaw_discord.core import Command
from openclaw_discord.phone_mic_gateway import build_phone_mic_html, handle_phone_mic_speech


class FakePipeline:
    def __init__(self):
        self.calls = []

    async def process_recognized_text(self, text, *, user_id):
        self.calls.append((text, user_id))
        command = Command(kind="mode", action="set", raw_text=text)
        return type("Result", (), {"ok": True, "message": "클로 모드가 켜졌습니다.", "command": command})()


class FakeRequest:
    def __init__(self, payload):
        self.payload = payload

    async def json(self):
        return self.payload


def test_phone_mic_html_contains_speech_controls():
    html = build_phone_mic_html()

    assert "SpeechRecognition" in html
    assert "/speech" in html
    assert "클로 온" in html
    assert "window.isSecureContext" in html
    assert "브라우저 상태" in html
    assert "start failed" in html


def test_phone_mic_speech_handler_processes_text_with_owner_id():
    pipeline = FakePipeline()

    response = asyncio.run(
        handle_phone_mic_speech(
            FakeRequest({"text": " 클로 온 "}),
            pipeline=pipeline,
            owner_user_id="owner-1",
            max_text_chars=40,
        )
    )

    assert response.status == 200
    assert json.loads(response.text) == {"ok": True, "message": "클로 모드가 켜졌습니다."}
    assert pipeline.calls == [("클로 온", "owner-1")]


def test_phone_mic_speech_handler_rejects_blank_text():
    pipeline = FakePipeline()

    response = asyncio.run(
        handle_phone_mic_speech(
            FakeRequest({"text": "   "}),
            pipeline=pipeline,
            owner_user_id="owner-1",
            max_text_chars=40,
        )
    )

    assert response.status == 400
    assert json.loads(response.text) == {"ok": False, "message": "No speech text was received."}
    assert pipeline.calls == []


def test_phone_mic_speech_handler_rejects_overlong_text():
    pipeline = FakePipeline()

    response = asyncio.run(
        handle_phone_mic_speech(
            FakeRequest({"text": "x" * 41}),
            pipeline=pipeline,
            owner_user_id="owner-1",
            max_text_chars=40,
        )
    )

    assert response.status == 413
    assert json.loads(response.text) == {"ok": False, "message": "Speech text is too long."}
    assert pipeline.calls == []
