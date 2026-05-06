from __future__ import annotations

from openclaw_discord.core import CommandContext, CommandResult, OpenClawCore
from openclaw_discord.discord_gateway import DiscordTextNotifier


class SpeechCommandPipeline:
    def __init__(self, *, core: OpenClawCore, text_notifier: DiscordTextNotifier) -> None:
        self.core = core
        self.text_notifier = text_notifier

    async def process_recognized_text(self, text: str, *, user_id: str) -> CommandResult:
        result = self.core.handle_text(text, CommandContext(user_id=user_id))
        await self.text_notifier.send(result.message)
        return result

