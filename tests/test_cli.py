import pytest

from openclaw_discord.__main__ import build_core, build_parser, build_voice_connection
from openclaw_discord.config import Settings
from openclaw_discord.controllers import DryRunController
from openclaw_discord.discord_gateway import DiscordBotVoiceConnection
from openclaw_discord.voice_receive import VoiceReceiveConnection


def test_cli_help_exits_cleanly(capsys):
    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--help"])

    assert exc_info.value.code == 0
    assert "OpenClaw Discord console mock" in capsys.readouterr().out


def test_cli_accepts_discord_mode_flag():
    parser = build_parser()

    args = parser.parse_args(["--discord"])

    assert args.discord is True


def test_cli_accepts_check_config_flag():
    parser = build_parser()

    args = parser.parse_args(["--check-config"])

    assert args.check_config is True


def test_cli_accepts_phone_mic_flag():
    parser = build_parser()

    args = parser.parse_args(["--discord", "--phone-mic", "--phone-mic-port", "8787"])

    assert args.discord is True
    assert args.phone_mic is True
    assert args.phone_mic_port == 8787


def test_build_core_uses_configured_controller_mode():
    settings = Settings(
        discord_bot_token="",
        guild_id="",
        owner_user_id="owner",
        voice_channel_id="",
        text_channel_id="",
        log_dir="logs",
        input_block_mode="simulate",
        max_text_input_chars=40,
        controller_mode="dry_run",
        enable_voice_receive=False,
        sandbox_root="",
    )

    core = build_core(settings, "owner")

    assert isinstance(core.controller, DryRunController)


def test_build_voice_connection_defaults_to_standard_discord_voice():
    settings = Settings(
        discord_bot_token="",
        guild_id="",
        owner_user_id="owner",
        voice_channel_id="",
        text_channel_id="",
        log_dir="logs",
        input_block_mode="simulate",
        max_text_input_chars=40,
        controller_mode="dry_run",
        enable_voice_receive=False,
        sandbox_root="",
    )

    connection = build_voice_connection(settings, bot=None, pipeline=None)

    assert isinstance(connection, DiscordBotVoiceConnection)


def test_build_voice_connection_uses_receive_adapter_when_enabled():
    settings = Settings(
        discord_bot_token="",
        guild_id="",
        owner_user_id="owner",
        voice_channel_id="",
        text_channel_id="",
        log_dir="logs",
        input_block_mode="simulate",
        max_text_input_chars=40,
        controller_mode="dry_run",
        enable_voice_receive=True,
        sandbox_root="",
    )

    connection = build_voice_connection(settings, bot=None, pipeline=object())

    assert isinstance(connection, VoiceReceiveConnection)
