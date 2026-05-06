from __future__ import annotations

from typing import Any

from discord.ext import commands

from openclaw_discord.speech_bridge import ThreadSafeSpeechBridge
from openclaw_discord.speech_pipeline import SpeechCommandPipeline
from openclaw_discord.speech_sink_factory import SpeechRecognitionSinkFactory
from openclaw_discord.discord_gateway import DiscordTextNotifier
from openclaw_discord.voice_recv_patch import patch_installed_voice_recv


class VoiceReceiveConnection:
    def __init__(
        self,
        *,
        bot: commands.Bot,
        voice_recv: Any | None = None,
        pipeline: SpeechCommandPipeline | None = None,
        text_notifier: DiscordTextNotifier | None = None,
        sink_factory_class: type[SpeechRecognitionSinkFactory] = SpeechRecognitionSinkFactory,
    ) -> None:
        self.bot = bot
        self.voice_recv = voice_recv or self._import_voice_recv()
        self.pipeline = pipeline
        self.text_notifier = text_notifier
        self.sink_factory_class = sink_factory_class
        self.voice_client: Any | None = None
        self._listening_started = False

    async def join(self, channel_id: str) -> None:
        channel = self.bot.get_channel(int(channel_id))
        if channel is None:
            raise ValueError(f"Discord voice channel not found: {channel_id}")

        existing_client = await self._prepare_existing_voice_client(channel)
        if existing_client is not None:
            self.voice_client = existing_client
            await self._start_listening_if_needed()
            return

        try:
            self.voice_client = await channel.connect(cls=self.voice_recv.VoiceRecvClient)
        except Exception:
            await self._cleanup_stale_voice_client(channel)
            self.voice_client = None
            self._listening_started = False
            raise

        await self._start_listening_if_needed()

    async def _start_listening_if_needed(self) -> None:
        if self._listening_started:
            return
        if self.pipeline is not None:
            import asyncio

            bridge = ThreadSafeSpeechBridge(loop=asyncio.get_running_loop(), pipeline=self.pipeline)
            sink = self.sink_factory_class(bridge=bridge, text_notifier=self.text_notifier).create()
            self.listen(sink)
            self._listening_started = True
            if self.text_notifier is not None:
                await self.text_notifier.send("음성 수신을 시작했습니다.")

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
            self._listening_started = False

    async def _prepare_existing_voice_client(self, channel: object) -> object | None:
        existing_client = self._find_guild_voice_client(channel)
        if existing_client is None:
            return None
        if self._is_connected(existing_client):
            return existing_client

        await self._disconnect(existing_client, force=True)
        return None

    async def _cleanup_stale_voice_client(self, channel: object) -> None:
        existing_client = self._find_guild_voice_client(channel)
        if existing_client is not None and not self._is_connected(existing_client):
            await self._disconnect(existing_client, force=True)

    def _find_guild_voice_client(self, channel: object) -> object | None:
        guild_id = getattr(getattr(channel, "guild", None), "id", None)
        if guild_id is None:
            return None

        for voice_client in getattr(self.bot, "voice_clients", []):
            client_guild_id = getattr(getattr(voice_client, "guild", None), "id", None)
            if client_guild_id == guild_id:
                return voice_client
        return None

    @staticmethod
    def _is_connected(voice_client: object) -> bool:
        is_connected = getattr(voice_client, "is_connected", None)
        if callable(is_connected):
            return bool(is_connected())
        return True

    @staticmethod
    async def _disconnect(voice_client: object, *, force: bool = False) -> None:
        disconnect = getattr(voice_client, "disconnect")
        try:
            await disconnect(force=force)
        except TypeError:
            await disconnect()

    @staticmethod
    def _import_voice_recv() -> Any:
        try:
            from discord.ext import voice_recv
            patch_installed_voice_recv()
        except ImportError as exc:
            raise RuntimeError(
                "discord-ext-voice-recv is required for Discord voice receive. "
                "Install it before enabling real voice recognition."
            ) from exc

        return voice_recv
