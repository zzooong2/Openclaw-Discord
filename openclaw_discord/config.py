from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    discord_bot_token: str
    guild_id: str
    owner_user_id: str
    voice_channel_id: str
    text_channel_id: str
    log_dir: str
    input_block_mode: str
    max_text_input_chars: int

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            discord_bot_token=os.getenv("DISCORD_BOT_TOKEN", ""),
            guild_id=os.getenv("DISCORD_GUILD_ID", ""),
            owner_user_id=os.getenv("DISCORD_OWNER_USER_ID", "console-owner"),
            voice_channel_id=os.getenv("DISCORD_VOICE_CHANNEL_ID", ""),
            text_channel_id=os.getenv("DISCORD_TEXT_CHANNEL_ID", ""),
            log_dir=os.getenv("OPENCLAW_LOG_DIR", "logs"),
            input_block_mode=os.getenv("OPENCLAW_INPUT_BLOCK_MODE", "simulate"),
            max_text_input_chars=int(os.getenv("OPENCLAW_MAX_TEXT_INPUT_CHARS", "40")),
        )
