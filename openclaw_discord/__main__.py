from __future__ import annotations

import argparse

from openclaw_discord.config import Settings
from openclaw_discord.config_validation import validate_discord_settings
from openclaw_discord.controller_factory import build_controller
from openclaw_discord.core import CommandContext, OpenClawCore
from openclaw_discord.discord_gateway import (
    DiscordBotTextNotifier,
    DiscordBotVoiceConnection,
    DiscordCommandService,
    build_discord_bot,
)
from openclaw_discord.input_blocking import SimulatedInputBlocker
from openclaw_discord.logging import OpenClawLogger
from openclaw_discord.speech_pipeline import SpeechCommandPipeline
from openclaw_discord.voice_receive import VoiceReceiveConnection


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenClaw Discord console mock")
    parser.add_argument(
        "--owner-user-id",
        help="Owner user id for console commands. Defaults to DISCORD_OWNER_USER_ID or console-owner.",
    )
    parser.add_argument("--discord", action="store_true", help="Run the Discord slash-command bot.")
    parser.add_argument("--check-config", action="store_true", help="Validate Discord .env settings and exit.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = Settings.from_env()
    owner_user_id = args.owner_user_id or settings.owner_user_id
    if args.check_config:
        return check_config(settings)

    if args.discord:
        run_discord(settings, owner_user_id)
        return 0

    run_console(settings, owner_user_id)
    return 0


def build_core(settings: Settings, owner_user_id: str) -> OpenClawCore:
    return OpenClawCore(
        owner_user_id=owner_user_id,
        controller=build_controller(settings),
        logger=OpenClawLogger(settings.log_dir),
        input_blocker=SimulatedInputBlocker(),
    )


def check_config(settings: Settings) -> int:
    issues = validate_discord_settings(settings)
    if not issues:
        print("Discord configuration is ready.")
        return 0

    print("Discord configuration has issues:")
    for issue in issues:
        print(f"- {issue.variable}: {issue.message}")
    return 1


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
    if not settings.guild_id or not settings.voice_channel_id or not settings.text_channel_id:
        raise SystemExit(
            "DISCORD_GUILD_ID, DISCORD_VOICE_CHANNEL_ID, and DISCORD_TEXT_CHANNEL_ID are required for --discord mode."
        )

    core = build_core(settings, owner_user_id)
    voice_connection = DiscordBotVoiceConnection()
    service = DiscordCommandService(
        owner_user_id=owner_user_id,
        voice_channel_id=settings.voice_channel_id,
        core=core,
        voice_connection=voice_connection,
    )
    bot = build_discord_bot(command_service=service, guild_id=settings.guild_id)
    service.text_notifier = DiscordBotTextNotifier(bot=bot, text_channel_id=settings.text_channel_id)
    pipeline = SpeechCommandPipeline(core=core, text_notifier=service.text_notifier)
    voice_connection = build_voice_connection(settings, bot=bot, pipeline=pipeline)
    service.voice_connection = voice_connection
    bot.run(settings.discord_bot_token)


def build_voice_connection(settings: Settings, *, bot: object | None, pipeline: object | None) -> object:
    if settings.enable_voice_receive:
        return VoiceReceiveConnection(bot=bot, pipeline=pipeline)

    return DiscordBotVoiceConnection(bot=bot)


if __name__ == "__main__":
    raise SystemExit(main())
