from __future__ import annotations

import argparse

from openclaw_discord.config import Settings
from openclaw_discord.controllers import DryRunController
from openclaw_discord.core import CommandContext, OpenClawCore
from openclaw_discord.logging import OpenClawLogger


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenClaw Discord console mock")
    parser.add_argument(
        "--owner-user-id",
        help="Owner user id for console commands. Defaults to DISCORD_OWNER_USER_ID or console-owner.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = Settings.from_env()
    owner_user_id = args.owner_user_id or settings.owner_user_id
    core = OpenClawCore(
        owner_user_id=owner_user_id,
        controller=DryRunController(),
        logger=OpenClawLogger(settings.log_dir),
    )
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


if __name__ == "__main__":
    raise SystemExit(main())

