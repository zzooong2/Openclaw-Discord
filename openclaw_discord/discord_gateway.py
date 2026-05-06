from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import discord
from discord import app_commands
from discord.ext import commands

from openclaw_discord.core import CommandContext, CommandResult, OpenClawCore


@dataclass(frozen=True)
class DiscordServiceResult:
    ok: bool
    message: str


@runtime_checkable
class DiscordVoiceConnection(Protocol):
    async def join(self, channel_id: str) -> None:
        """Join the configured Discord voice channel."""

    async def leave(self) -> None:
        """Leave the current Discord voice channel."""


@runtime_checkable
class DiscordTextNotifier(Protocol):
    async def send(self, message: str) -> None:
        """Send a user-facing status message."""


class DiscordCommandService:
    def __init__(
        self,
        *,
        owner_user_id: str,
        voice_channel_id: str,
        text_channel_id: str = "",
        core: OpenClawCore,
        voice_connection: DiscordVoiceConnection,
        text_notifier: DiscordTextNotifier | None = None,
    ) -> None:
        self.owner_user_id = owner_user_id
        self.voice_channel_id = voice_channel_id
        self.text_channel_id = text_channel_id
        self.core = core
        self.voice_connection = voice_connection
        self.text_notifier = text_notifier

    async def join(self, user_id: str) -> DiscordServiceResult:
        blocked = self._reject_if_not_owner(user_id)
        if blocked is not None:
            return blocked
        if not self.voice_channel_id:
            return await self._finish(DiscordServiceResult(False, "차단: 음성 채널이 설정되지 않았습니다."), notify_blocked=True)

        await self.voice_connection.join(self.voice_channel_id)
        return await self._finish(DiscordServiceResult(True, "음성 채널에 연결했습니다."))

    async def leave(self, user_id: str) -> DiscordServiceResult:
        blocked = self._reject_if_not_owner(user_id)
        if blocked is not None:
            return blocked

        await self.voice_connection.leave()
        return await self._finish(DiscordServiceResult(True, "음성 채널에서 나왔습니다."))

    async def voice_mode_off(self, user_id: str) -> DiscordServiceResult:
        blocked = self._reject_if_not_owner(user_id)
        if blocked is not None:
            return blocked

        result: CommandResult = self.core.handle_text("클로 오프", CommandContext(user_id=user_id))
        return await self._finish(DiscordServiceResult(result.ok, result.message))

    async def debug_speech(self, user_id: str, text: str) -> DiscordServiceResult:
        blocked = self._reject_if_not_owner(user_id)
        if blocked is not None:
            return blocked

        result: CommandResult = self.core.handle_text(text, CommandContext(user_id=user_id))
        return await self._finish(DiscordServiceResult(result.ok, result.message), notify_blocked=True)

    async def process_chat_message(
        self,
        *,
        user_id: str,
        channel_id: str,
        content: str,
        author_is_bot: bool = False,
    ) -> DiscordServiceResult | None:
        if author_is_bot or channel_id != self.text_channel_id or user_id != self.owner_user_id:
            return None

        result: CommandResult = self.core.handle_text(content, CommandContext(user_id=user_id))
        return await self._finish(DiscordServiceResult(result.ok, result.message), notify_blocked=True)

    def _reject_if_not_owner(self, user_id: str) -> DiscordServiceResult | None:
        if user_id != self.owner_user_id:
            return DiscordServiceResult(False, "차단: 허용되지 않은 사용자입니다.")
        return None

    async def _finish(self, result: DiscordServiceResult, *, notify_blocked: bool = False) -> DiscordServiceResult:
        should_notify = result.ok or notify_blocked
        if should_notify and self.text_notifier is not None:
            await self.text_notifier.send(result.message)
        return result


class DiscordBotVoiceConnection:
    def __init__(self, *, bot: commands.Bot | None = None) -> None:
        self.bot = bot
        self.voice_client: object | None = None

    def set_bot(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def join(self, channel_id: str) -> None:
        if self.bot is None:
            raise RuntimeError("Discord bot is not attached to the voice connection.")

        channel = self.bot.get_channel(int(channel_id))
        if channel is None:
            raise ValueError(f"Discord voice channel not found: {channel_id}")

        existing_client = await self._prepare_existing_voice_client(channel)
        if existing_client is not None:
            self.voice_client = existing_client
            return

        try:
            self.voice_client = await channel.connect()
        except Exception:
            await self._cleanup_stale_voice_client(channel)
            self.voice_client = None
            raise

    async def leave(self) -> None:
        if self.voice_client is not None:
            await self.voice_client.disconnect()
            self.voice_client = None

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
        if self.bot is None:
            return None
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


class DiscordBotTextNotifier:
    def __init__(self, *, bot: commands.Bot, text_channel_id: str) -> None:
        self.bot = bot
        self.text_channel_id = text_channel_id

    async def send(self, message: str) -> None:
        channel = self.bot.get_channel(int(self.text_channel_id))
        if channel is None:
            raise ValueError(f"Discord text channel not found: {self.text_channel_id}")
        if not hasattr(channel, "send"):
            raise TypeError(f"Discord text channel is not sendable: {self.text_channel_id}")

        await channel.send(message)


def build_discord_bot(*, command_service: DiscordCommandService, guild_id: str) -> commands.Bot:
    intents = discord.Intents.default()
    intents.voice_states = True
    intents.messages = True
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    guild = discord.Object(id=int(guild_id)) if guild_id.isdigit() else None

    async def respond(interaction: discord.Interaction, result: DiscordServiceResult) -> None:
        await interaction.response.send_message(result.message, ephemeral=not result.ok)

    @bot.tree.command(name="join", description="Join the configured OpenClaw voice channel.", guild=guild)
    async def join_command(interaction: discord.Interaction) -> None:
        result = await command_service.join(str(interaction.user.id))
        await respond(interaction, result)

    @bot.tree.command(name="leave", description="Leave the current OpenClaw voice channel.", guild=guild)
    async def leave_command(interaction: discord.Interaction) -> None:
        result = await command_service.leave(str(interaction.user.id))
        await respond(interaction, result)

    @bot.tree.command(name="debug-speech", description="Process text as if it came from speech recognition.", guild=guild)
    async def debug_speech_command(interaction: discord.Interaction, text: str) -> None:
        result = await command_service.debug_speech(str(interaction.user.id), text)
        await respond(interaction, result)

    voice_mode_group = app_commands.Group(name="voice-mode", description="Control OpenClaw voice mode.", guild_ids=None)

    @voice_mode_group.command(name="off", description="Emergency-disable OpenClaw voice mode.")
    async def voice_mode_off_command(interaction: discord.Interaction) -> None:
        result = await command_service.voice_mode_off(str(interaction.user.id))
        await respond(interaction, result)

    bot.tree.add_command(voice_mode_group, guild=guild)

    @bot.event
    async def on_ready() -> None:
        await sync_application_commands(bot, guild_id)

    @bot.event
    async def on_message(message: discord.Message) -> None:
        await command_service.process_chat_message(
            user_id=str(message.author.id),
            channel_id=str(message.channel.id),
            content=message.content,
            author_is_bot=message.author.bot,
        )
        await bot.process_commands(message)

    return bot


async def sync_application_commands(bot: commands.Bot, guild_id: str) -> None:
    guild = discord.Object(id=int(guild_id)) if guild_id.isdigit() else None
    await bot.tree.sync(guild=guild)
