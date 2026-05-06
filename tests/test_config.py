from openclaw_discord.config import Settings


def test_settings_reads_required_values_from_environment(monkeypatch):
    monkeypatch.setattr("openclaw_discord.config.load_dotenv", lambda: None)
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token-1")
    monkeypatch.setenv("DISCORD_GUILD_ID", "guild-1")
    monkeypatch.setenv("DISCORD_OWNER_USER_ID", "owner-1")
    monkeypatch.setenv("DISCORD_VOICE_CHANNEL_ID", "voice-1")
    monkeypatch.setenv("DISCORD_TEXT_CHANNEL_ID", "text-1")
    monkeypatch.setenv("OPENCLAW_LOG_DIR", "custom-logs")
    monkeypatch.setenv("OPENCLAW_MAX_TEXT_INPUT_CHARS", "12")
    monkeypatch.delenv("OPENCLAW_ENABLE_VOICE_RECEIVE", raising=False)

    settings = Settings.from_env()

    assert settings.discord_bot_token == "token-1"
    assert settings.guild_id == "guild-1"
    assert settings.owner_user_id == "owner-1"
    assert settings.voice_channel_id == "voice-1"
    assert settings.text_channel_id == "text-1"
    assert settings.log_dir == "custom-logs"
    assert settings.max_text_input_chars == 12
    assert settings.controller_mode == "dry_run"
    assert settings.enable_voice_receive is False


def test_settings_uses_safe_console_defaults(monkeypatch):
    monkeypatch.setattr("openclaw_discord.config.load_dotenv", lambda: None)
    monkeypatch.delenv("DISCORD_OWNER_USER_ID", raising=False)
    monkeypatch.delenv("OPENCLAW_LOG_DIR", raising=False)
    monkeypatch.delenv("OPENCLAW_INPUT_BLOCK_MODE", raising=False)

    settings = Settings.from_env()

    assert settings.owner_user_id == "console-owner"
    assert settings.log_dir == "logs"
    assert settings.input_block_mode == "simulate"


def test_settings_reads_controller_mode(monkeypatch):
    monkeypatch.setenv("OPENCLAW_CONTROLLER_MODE", "windows")

    settings = Settings.from_env()

    assert settings.controller_mode == "windows"


def test_settings_reads_voice_receive_flag(monkeypatch):
    monkeypatch.setenv("OPENCLAW_ENABLE_VOICE_RECEIVE", "true")

    settings = Settings.from_env()

    assert settings.enable_voice_receive is True
