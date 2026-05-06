from __future__ import annotations

import asyncio
from concurrent.futures import Future

from openclaw_discord.speech_pipeline import SpeechCommandPipeline


class ThreadSafeSpeechBridge:
    def __init__(self, *, loop: asyncio.AbstractEventLoop, pipeline: SpeechCommandPipeline) -> None:
        self.loop = loop
        self.pipeline = pipeline

    def submit(self, text: str, *, user_id: str) -> Future | None:
        normalized = text.strip()
        if not normalized:
            return None

        coroutine = self.pipeline.process_recognized_text(normalized, user_id=user_id)
        return asyncio.run_coroutine_threadsafe(coroutine, self.loop)

