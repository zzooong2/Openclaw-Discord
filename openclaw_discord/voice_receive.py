from __future__ import annotations

from typing import Any

from discord.ext import commands

from openclaw_discord.speech_bridge import ThreadSafeSpeechBridge
from openclaw_discord.speech_pipeline import SpeechCommandPipeline
from openclaw_discord.speech_sink_factory import SpeechRecognitionSinkFactory


class VoiceReceiveConnection:
    def __init__(
        self,
        *,
        bot: commands.Bot,
        voice_recv: Any | None = None,
        pipeline: SpeechCommandPipeline | None = None,
        sink_factory_class: type[SpeechRecognitionSinkFactory] = SpeechRecognitionSinkFactory,
    ) -> None:
        self.bot = bot
        self.voice_recv = voice_recv or self._import_voice_recv()
        self.pipeline = pipeline
        self.sink_factory_class = sink_factory_class
        self.voice_client: Any | None = None

    async def join(self, channel_id: str) -> None:
        channel = self.bot.get_channel(int(channel_id))
        if channel is None:
            raise ValueError(f"Discord voice channel not found: {channel_id}")

        self.voice_client = await channel.connect(cls=self.voice_recv.VoiceRecvClient)
        if self.pipeline is not None:
            import asyncio

            bridge = ThreadSafeSpeechBridge(loop=asyncio.get_running_loop(), pipeline=self.pipeline)
            sink = self.sink_factory_class(bridge=bridge).create()
            self.listen(sink)

    def listen(self, sink: object) -> None:
        if self.voice_client is None:
            raise RuntimeError("Voice receive client is not connected.")

        self.voice_client.listen(sink)

    def stop_listening(self) -> None:
        if self.voice_client is not None:
            self.voice_client.stop_listening()

    async def leave(self) -> None:
        if self.voice_client is not None:
            await self.voice_client.disconnect()
            self.voice_client = None

    @staticmethod
    def _import_voice_recv() -> Any:
        try:
            from discord.ext import voice_recv
        except ImportError as exc:
            raise RuntimeError(
                "discord-ext-voice-recv is required for Discord voice receive. "
                "Install it before enabling real voice recognition."
            ) from exc

        return voice_recv
