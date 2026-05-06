from __future__ import annotations

from dataclasses import dataclass

from openclaw_discord.config import Settings


@dataclass(frozen=True)
class ConfigIssue:
    variable: str
    message: str


DISCORD_ID_FIELDS = {
    "DISCORD_GUILD_ID": "guild_id",
    "DISCORD_OWNER_USER_ID": "owner_user_id",
    "DISCORD_TEXT_CHANNEL_ID": "text_channel_id",
}


def validate_discord_settings(settings: Settings) -> list[ConfigIssue]:
    issues: list[ConfigIssue] = []
    if not settings.discord_bot_token:
        issues.append(ConfigIssue("DISCORD_BOT_TOKEN", "Discord bot token is required."))

    for variable, field_name in DISCORD_ID_FIELDS.items():
        value = getattr(settings, field_name)
        if not value:
            issues.append(ConfigIssue(variable, "Discord ID is required."))
        elif not value.isdigit():
            issues.append(ConfigIssue(variable, "Discord ID must be numeric."))

    if settings.voice_channel_id and not settings.voice_channel_id.isdigit():
        issues.append(ConfigIssue("DISCORD_VOICE_CHANNEL_ID", "Discord ID must be numeric."))
    elif settings.enable_voice_receive and not settings.voice_channel_id:
        issues.append(ConfigIssue("DISCORD_VOICE_CHANNEL_ID", "Discord ID is required when voice receive is enabled."))

    return issues
