from openclaw_discord.config import Settings
from openclaw_discord.config_validation import ConfigIssue, validate_discord_settings


def make_settings(**overrides):
    values = {
        "discord_bot_token": "token",
        "guild_id": "123",
        "owner_user_id": "456",
        "voice_channel_id": "789",
        "text_channel_id": "111",
        "log_dir": "logs",
        "input_block_mode": "simulate",
        "max_text_input_chars": 40,
        "controller_mode": "dry_run",
        "enable_voice_receive": False,
    }
    values.update(overrides)
    return Settings(**values)


def test_validate_discord_settings_accepts_complete_numeric_ids():
    assert validate_discord_settings(make_settings()) == []


def test_validate_discord_settings_reports_missing_token():
    issues = validate_discord_settings(make_settings(discord_bot_token=""))

    assert issues == [ConfigIssue("DISCORD_BOT_TOKEN", "Discord bot token is required.")]


def test_validate_discord_settings_reports_non_numeric_ids():
    issues = validate_discord_settings(make_settings(guild_id="abc", voice_channel_id="voice"))

    assert issues == [
        ConfigIssue("DISCORD_GUILD_ID", "Discord ID must be numeric."),
        ConfigIssue("DISCORD_VOICE_CHANNEL_ID", "Discord ID must be numeric."),
    ]
