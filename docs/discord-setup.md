# Discord Setup Checklist

Use the shared server invite as the target server reference:

```text
https://discord.gg/VGySqE2y
```

The bot cannot use the invite URL directly. It needs numeric Discord IDs in `.env`.

## 1. Enable Developer Mode

In Discord:

1. Open User Settings.
2. Open Advanced.
3. Enable Developer Mode.

## 2. Collect IDs

Right-click each target and copy its ID:

- Server -> `DISCORD_GUILD_ID`
- Your Discord user -> `DISCORD_OWNER_USER_ID`
- Target voice channel -> `DISCORD_VOICE_CHANNEL_ID`
- Target text channel -> `DISCORD_TEXT_CHANNEL_ID`

## 3. Create `.env`

Copy `.env.example` to `.env`, then fill in real values:

```dotenv
DISCORD_BOT_TOKEN=replace-me
DISCORD_GUILD_ID=123456789012345678
DISCORD_OWNER_USER_ID=123456789012345678
DISCORD_VOICE_CHANNEL_ID=123456789012345678
DISCORD_TEXT_CHANNEL_ID=123456789012345678

OPENCLAW_INPUT_BLOCK_MODE=simulate
OPENCLAW_CONTROLLER_MODE=dry_run
OPENCLAW_ENABLE_VOICE_RECEIVE=false
OPENCLAW_LOG_DIR=logs
OPENCLAW_MOUSE_STEP=120
OPENCLAW_MOUSE_SMALL_STEP=30
OPENCLAW_MAX_TEXT_INPUT_CHARS=40
```

Keep these safe:

- Do not commit `.env`.
- Do not paste the bot token into Discord chat.
- Start with `OPENCLAW_CONTROLLER_MODE=dry_run`.
- Start with `OPENCLAW_ENABLE_VOICE_RECEIVE=false`.

## 4. Validate Config

```bash
python -m openclaw_discord --check-config
```

Expected:

```text
Discord configuration is ready.
```

## 5. Start Discord Bot

```bash
python -m openclaw_discord --discord
```

In Discord, test slash commands:

- `/join`
- `/debug-speech text:클로 온`
- `/voice-mode off`
- `/leave`

## 6. Enable Voice Receive Later

Only after slash commands work:

```bash
python -m pip install .[voice]
```

Then set:

```dotenv
OPENCLAW_ENABLE_VOICE_RECEIVE=true
```

After that, restart the bot and test saying:

```text
클로 온
```

