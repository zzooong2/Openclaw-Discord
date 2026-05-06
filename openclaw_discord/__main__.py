from __future__ import annotations

import argparse

from openclaw_discord.config import Settings
from openclaw_discord.controllers import DryRunController
from openclaw_discord.core import CommandContext, OpenClawCore
from openclaw_discord.discord_gateway import (
    DiscordBotVoiceConnection,
    DiscordCommandService,
    build_discord_bot,
)
from openclaw_discord.input_blocking import SimulatedInputBlocker
from openclaw_discord.logging import OpenClawLogger


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenClaw Discord console mock")
    parser.add_argument(
        "--owner-user-id",
        help="Owner user id for console commands. Defaults to DISCORD_OWNER_USER_ID or console-owner.",
    )
    parser.add_argument("--discord", action="store_true", help="Run the Discord slash-command bot.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = Settings.from_env()
    owner_user_id = args.owner_user_id or settings.owner_user_id
    if args.discord:
        run_discord(settings, owner_user_id)
        return 0

    run_console(settings, owner_user_id)
    return 0


def build_core(settings: Settings, owner_user_id: str) -> OpenClawCore:
    return OpenClawCore(
        owner_user_id=owner_user_id,
        controller=DryRunController(),
        logger=OpenClawLogger(settings.log_dir),
        input_blocker=SimulatedInputBlocker(),
    )


def run_console(settings: Settings, owner_user_id: str) -> int:
    core = build_core(settings, owner_user_id)
    context = CommandContext(user_id=owner_user_id)

    print("OpenClaw Discord console mock. Type Korean commands, or 'exit' to quit.")
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if text.lower() == "exit":
            return 0

        if not text:
            continue

        result = core.handle_text(text, context)
        print(result.message)


def run_discord(settings: Settings, owner_user_id: str) -> None:
    if not settings.discord_bot_token:
        raise SystemExit("DISCORD_BOT_TOKEN is required for --discord mode.")
    if not settings.guild_id or not settings.voice_channel_id:
        raise SystemExit("DISCORD_GUILD_ID and DISCORD_VOICE_CHANNEL_ID are required for --discord mode.")

    core = build_core(settings, owner_user_id)
    voice_connection = DiscordBotVoiceConnection()
    service = DiscordCommandService(
        owner_user_id=owner_user_id,
        voice_channel_id=settings.voice_channel_id,
        core=core,
        voice_connection=voice_connection,
    )
    bot = build_discord_bot(command_service=service, guild_id=settings.guild_id)
    voice_connection.set_bot(bot)
    bot.run(settings.discord_bot_token)


if __name__ == "__main__":
    raise SystemExit(main())
