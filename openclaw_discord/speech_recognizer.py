from __future__ import annotations

from typing import Protocol


class SpeechRecognizer(Protocol):
    def recognize(self, text: str) -> str | None:
        """Return recognized command text, or None when the text should be ignored."""


class ExactPhraseRecognizer:
    def __init__(self, allowed_phrases: set[str]) -> None:
        self.allowed_phrases = {" ".join(phrase.strip().split()) for phrase in allowed_phrases}

    def recognize(self, text: str) -> str | None:
        normalized = " ".join(text.strip().split())
        if normalized in self.allowed_phrases:
            return normalized
        return None

