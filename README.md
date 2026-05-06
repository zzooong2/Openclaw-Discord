# OpenClaw Discord

OpenClaw Discord is a Windows-first Discord voice control project. The goal is to let one approved Discord user control a PC by voice while keeping the control surface small, explicit, and recoverable.

The first milestone is intentionally conservative: fixed Korean commands, a clear voice-control mode, Discord text feedback, complete logging, and emergency off switches before broad automation is added.

## MVP Scope

- Discord bot listens only in one configured voice channel.
- Only one configured Discord user can issue commands.
- Voice control mode is toggled with fixed Korean phrases:
  - `클로 온`
  - `클로 오프`
- When voice control mode is on, physical keyboard and mouse input will eventually be blocked.
- Early development uses input-block simulation logs before real input blocking is enabled.
- Emergency off paths:
  - `Ctrl + Alt + F12`
  - Discord slash command `/voice-mode off`
- Discord slash commands:
  - `/join`
  - `/leave`
  - `/voice-mode off`
- Discord text responses are sent to one configured text channel.
- Logs are stored as both human-readable text and JSONL.

## Command Categories

The MVP supports fixed Korean commands only. Aliases are intentionally disabled at first.

- Mode commands: turn OpenClaw voice control on or off.
- App commands: open or close Notepad, Calculator, Chrome, and File Explorer.
- Mouse commands: relative movement, screen-position movement, left click, right click, double click.
- Keyboard commands: shortcuts and short text input.
- Confirmation commands: confirm selected commands such as closing an app or window.

Risky commands such as file deletion, destructive system changes, payments, credential handling, or arbitrary shell execution are out of MVP scope.

## Planned Tech Stack

- Python
- `python -m openclaw_discord` entrypoint
- `discord.py` or a compatible Discord library with slash command support
- Windows automation libraries first, Windows API only where needed
- `pytest` for parser, mode, safety, and logging tests
- `.env` for all runtime configuration

## Development Order

1. Document the design, command list, environment variables, and safety boundaries.
2. Build OpenClaw Core with console-based mock speech input.
3. Add fixed Korean command parsing.
4. Add mode, permission, confirmation, and safety checks.
5. Add structured logging.
6. Add Windows app, mouse, and keyboard execution adapters.
7. Add Discord slash commands and text-channel feedback.
8. Add Discord voice-channel connection and pluggable STT interface.
9. Reach the first MVP success: saying `클로 온` through Discord voice turns on voice control mode.
10. Add input-block simulation, then real keyboard/mouse blocking with emergency off paths.

## Configuration

Runtime secrets and IDs will be read from `.env`. See `docs/env.md` for the planned variable list.

Never commit Discord bot tokens, user tokens, API keys, or machine-specific secrets.

The target Discord server invite shared during planning is `https://discord.gg/VGySqE2y`. The bot runtime still needs numeric Discord IDs in `.env`; the invite URL is not enough for channel-scoped slash commands or voice-channel joins.

## Running

Console mock mode:

```bash
python -m openclaw_discord
```

Discord slash-command mode:

```bash
python -m openclaw_discord --discord
```

Check Discord `.env` values before starting the bot:

```bash
python -m openclaw_discord --check-config
```

By default, commands use `OPENCLAW_CONTROLLER_MODE=dry_run`. Set `OPENCLAW_CONTROLLER_MODE=windows` only when you are ready for the bot to perform real Windows app, mouse, and keyboard actions.

Current Discord commands:

- `/join`
- `/leave`
- `/voice-mode off`
- `/debug-speech text:<command>` for owner-only pipeline testing before real STT is enabled

Discord voice receive is isolated behind an optional adapter. See `docs/voice-receive.md` before enabling real voice recognition.

For the Discord server setup checklist, see `docs/discord-setup.md`.

## Safety Notes

OpenClaw must prefer no action over uncertain action. If a voice command is not recognized exactly, it should be rejected and logged. If voice control mode is off, PC-control commands should be blocked. If an emergency off path is triggered, the system should immediately return to normal keyboard and mouse behavior.
