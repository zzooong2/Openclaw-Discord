import pytest

from openclaw_discord.__main__ import build_core, build_parser
from openclaw_discord.config import Settings
from openclaw_discord.controllers import DryRunController


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
    )

    core = build_core(settings, "owner")

    assert isinstance(core.controller, DryRunController)
