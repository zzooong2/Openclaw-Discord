from __future__ import annotations

from typing import Any

from openclaw_discord.speech_bridge import ThreadSafeSpeechBridge


class SpeechRecognitionSinkFactory:
    def __init__(
        self,
        *,
        bridge: ThreadSafeSpeechBridge,
        speech_recognition_module: Any | None = None,
        recognizer_name: str = "google",
        phrase_time_limit: int = 3,
    ) -> None:
        self.bridge = bridge
        self.speech_recognition_module = speech_recognition_module or self._import_speech_recognition_module()
        self.recognizer_name = recognizer_name
        self.phrase_time_limit = phrase_time_limit

    def create(self) -> object:
        def text_cb(user: object, text: str) -> None:
            self.bridge.submit(text, user_id=str(user.id))

        return self.speech_recognition_module.SpeechRecognitionSink(
            text_cb=text_cb,
            default_recognizer=self.recognizer_name,
            phrase_time_limit=self.phrase_time_limit,
        )

    @staticmethod
    def _import_speech_recognition_module() -> Any:
        try:
            from discord.ext.voice_recv.extras import speechrecognition
        except (ImportError, RuntimeError) as exc:
            raise RuntimeError(
                "discord-ext-voice-recv with SpeechRecognition support is required for STT sinks. "
                "Install the voice extra before enabling real speech recognition."
            ) from exc

        return speechrecognition

