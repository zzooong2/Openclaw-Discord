import asyncio

from openclaw_discord.controllers import RecordedController
from openclaw_discord.core import CommandContext, OpenClawCore
from openclaw_discord.discord_gateway import (
    DiscordBotTextNotifier,
    DiscordBotVoiceConnection,
    DiscordCommandService,
    DiscordVoiceConnection,
    build_discord_bot,
    sync_application_commands,
)
from openclaw_discord.input_blocking import SimulatedInputBlocker


OWNER_ID = "owner-1"
VOICE_CHANNEL_ID = "voice-1"
TEXT_CHANNEL_ID = "text-1"


class FakeVoiceConnection:
    def __init__(self):
        self.joined = []
        self.left = 0

    async def join(self, channel_id):
        self.joined.append(channel_id)

    async def leave(self):
        self.left += 1


class FakeTextNotifier:
    def __init__(self):
        self.messages = []

    async def send(self, message):
        self.messages.append(message)


class FakeDiscordVoiceClient:
    def __init__(self):
        self.disconnected = False
        self.force_disconnect = None
        self.connected = True
        self.guild = None

    def is_connected(self):
        return self.connected

    async def disconnect(self, *, force=False):
        self.disconnected = True
        self.force_disconnect = force
        self.connected = False


class FakeDiscordVoiceChannel:
    def __init__(self, *, connect_error=None):
        self.connected = 0
        self.voice_client = FakeDiscordVoiceClient()
        self.connect_error = connect_error
        self.guild = type("Guild", (), {"id": 456})()
        self.voice_client.guild = self.guild

    async def connect(self):
        self.connected += 1
        if self.connect_error is not None:
            raise self.connect_error
        return self.voice_client


class FakeDiscordBot:
    def __init__(self, channel, *, voice_clients=None):
        self.channel = channel
        self.voice_clients = voice_clients or []

    def get_channel(self, channel_id):
        if channel_id == 123:
            return self.channel
        return None


class FakeCommandTree:
    def __init__(self):
        self.synced_guilds = []

    async def sync(self, *, guild=None):
        self.synced_guilds.append(guild.id if guild else None)


class FakeSyncBot:
    def __init__(self):
        self.tree = FakeCommandTree()


class FakeDiscordTextChannel:
    def __init__(self):
        self.messages = []

    async def send(self, message):
        self.messages.append(message)


class FakeDiscordCategoryChannel:
    pass


def build_service():
    blocker = SimulatedInputBlocker()
    core = OpenClawCore(
        owner_user_id=OWNER_ID,
        controller=RecordedController(),
        input_blocker=blocker,
    )
    voice = FakeVoiceConnection()
    notifier = FakeTextNotifier()
    service = DiscordCommandService(
        owner_user_id=OWNER_ID,
        voice_channel_id=VOICE_CHANNEL_ID,
        text_channel_id=TEXT_CHANNEL_ID,
        core=core,
        voice_connection=voice,
        text_notifier=notifier,
    )
    return service, core, blocker, voice, notifier


def test_join_connects_configured_voice_channel():
    service, _, _, voice, notifier = build_service()

    result = asyncio.run(service.join(OWNER_ID))

    assert result.ok is True
    assert result.message == "음성 채널에 연결했습니다."
    assert voice.joined == [VOICE_CHANNEL_ID]
    assert notifier.messages == ["음성 채널에 연결했습니다."]


def test_join_reports_missing_voice_channel():
    service, _, _, voice, notifier = build_service()
    service.voice_channel_id = ""

    result = asyncio.run(service.join(OWNER_ID))

    assert result.ok is False
    assert result.message == "차단: 음성 채널이 설정되지 않았습니다."
    assert voice.joined == []
    assert notifier.messages == ["차단: 음성 채널이 설정되지 않았습니다."]


def test_leave_disconnects_voice_channel():
    service, _, _, voice, notifier = build_service()

    result = asyncio.run(service.leave(OWNER_ID))

    assert result.ok is True
    assert result.message == "음성 채널에서 나왔습니다."
    assert voice.left == 1
    assert notifier.messages == ["음성 채널에서 나왔습니다."]


def test_voice_mode_off_turns_core_and_blocker_off():
    service, core, blocker, _, notifier = build_service()
    core.handle_text("클로 온", context=CommandContext(user_id=OWNER_ID))

    result = asyncio.run(service.voice_mode_off(OWNER_ID))

    assert result.ok is True
    assert result.message == "클로 모드가 꺼졌습니다."
    assert core.voice_mode_enabled is False
    assert blocker.enabled is False
    assert notifier.messages == ["클로 모드가 꺼졌습니다."]


def test_debug_speech_processes_text_like_recognized_voice():
    service, core, blocker, _, notifier = build_service()

    result = asyncio.run(service.debug_speech(OWNER_ID, "클로 온"))

    assert result.ok is True
    assert result.message == "클로 모드가 켜졌습니다."
    assert core.voice_mode_enabled is True
    assert blocker.enabled is True
    assert notifier.messages == ["클로 모드가 켜졌습니다."]


def test_chat_message_processes_owner_message_in_configured_text_channel():
    service, core, blocker, _, notifier = build_service()

    result = asyncio.run(service.process_chat_message(user_id=OWNER_ID, channel_id=TEXT_CHANNEL_ID, content="클로 켜줘"))

    assert result is not None
    assert result.ok is True
    assert result.message == "클로 모드가 켜졌습니다."
    assert core.voice_mode_enabled is True
    assert blocker.enabled is True
    assert notifier.messages == ["클로 모드가 켜졌습니다."]


def test_chat_message_ignores_other_text_channels():
    service, _, _, _, notifier = build_service()

    result = asyncio.run(service.process_chat_message(user_id=OWNER_ID, channel_id="other-channel", content="클로 켜줘"))

    assert result is None
    assert notifier.messages == []


def test_chat_message_ignores_non_owner_messages_without_replying():
    service, _, _, _, notifier = build_service()

    result = asyncio.run(service.process_chat_message(user_id="someone-else", channel_id=TEXT_CHANNEL_ID, content="클로 켜줘"))

    assert result is None
    assert notifier.messages == []


def test_chat_message_reports_blocked_unknown_owner_message():
    service, _, _, _, notifier = build_service()

    result = asyncio.run(service.process_chat_message(user_id=OWNER_ID, channel_id=TEXT_CHANNEL_ID, content="오늘 날씨 알려줘"))

    assert result is not None
    assert result.ok is False
    assert result.message == "차단: 알 수 없는 명령입니다."
    assert notifier.messages == ["차단: 알 수 없는 명령입니다."]


def test_rejects_non_owner_slash_commands():
    service, _, _, voice, notifier = build_service()

    result = asyncio.run(service.join("someone-else"))

    assert result.ok is False
    assert result.message == "차단: 허용되지 않은 사용자입니다."
    assert voice.joined == []
    assert notifier.messages == []


def test_voice_connection_protocol_is_runtime_checkable():
    assert isinstance(FakeVoiceConnection(), DiscordVoiceConnection)


def test_build_discord_bot_exposes_required_command_names():
    service, _, _, _, _ = build_service()

    bot = build_discord_bot(command_service=service, guild_id="guild-1")

    assert sorted(command.name for command in bot.tree.get_commands()) == ["debug-speech", "join", "leave", "voice-mode"]


def test_build_discord_bot_enables_message_content_intent():
    service, _, _, _, _ = build_service()

    bot = build_discord_bot(command_service=service, guild_id="guild-1")

    assert bot.intents.message_content is True


def test_discord_bot_voice_connection_joins_channel():
    channel = FakeDiscordVoiceChannel()
    connection = DiscordBotVoiceConnection(bot=FakeDiscordBot(channel))

    asyncio.run(connection.join("123"))

    assert channel.connected == 1


def test_discord_bot_voice_connection_reuses_existing_connected_voice_client():
    channel = FakeDiscordVoiceChannel()
    voice_client = channel.voice_client
    connection = DiscordBotVoiceConnection(bot=FakeDiscordBot(channel, voice_clients=[voice_client]))

    asyncio.run(connection.join("123"))

    assert channel.connected == 0
    assert connection.voice_client is voice_client


def test_discord_bot_voice_connection_cleans_stale_voice_client_before_connecting():
    channel = FakeDiscordVoiceChannel()
    stale_client = FakeDiscordVoiceClient()
    stale_client.connected = False
    stale_client.guild = channel.guild
    connection = DiscordBotVoiceConnection(bot=FakeDiscordBot(channel, voice_clients=[stale_client]))

    asyncio.run(connection.join("123"))

    assert stale_client.disconnected is True
    assert stale_client.force_disconnect is True
    assert channel.connected == 1
    assert connection.voice_client is channel.voice_client


def test_discord_bot_voice_connection_leaves_current_channel():
    channel = FakeDiscordVoiceChannel()
    connection = DiscordBotVoiceConnection(bot=FakeDiscordBot(channel))
    asyncio.run(connection.join("123"))

    asyncio.run(connection.leave())

    assert channel.voice_client.disconnected is True


def test_discord_bot_text_notifier_sends_to_configured_channel():
    channel = FakeDiscordTextChannel()
    notifier = DiscordBotTextNotifier(bot=FakeDiscordBot(channel), text_channel_id="123")

    asyncio.run(notifier.send("테스트 메시지"))

    assert channel.messages == ["테스트 메시지"]


def test_discord_bot_text_notifier_rejects_non_text_channel():
    notifier = DiscordBotTextNotifier(bot=FakeDiscordBot(FakeDiscordCategoryChannel()), text_channel_id="123")

    try:
        asyncio.run(notifier.send("테스트 메시지"))
    except TypeError as exc:
        assert str(exc) == "Discord text channel is not sendable: 123"
    else:
        raise AssertionError("Expected TypeError")


def test_sync_application_commands_uses_configured_guild_id():
    bot = FakeSyncBot()

    asyncio.run(sync_application_commands(bot, "123"))

    assert bot.tree.synced_guilds == [123]
