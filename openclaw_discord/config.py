from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    owner_user_id: str
    log_dir: str
    input_block_mode: str
    max_text_input_chars: int

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            owner_user_id=os.getenv("DISCORD_OWNER_USER_ID", "console-owner"),
            log_dir=os.getenv("OPENCLAW_LOG_DIR", "logs"),
            input_block_mode=os.getenv("OPENCLAW_INPUT_BLOCK_MODE", "simulate"),
            max_text_input_chars=int(os.getenv("OPENCLAW_MAX_TEXT_INPUT_CHARS", "40")),
        )

