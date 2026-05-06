# OpenClaw Discord

OpenClaw Discord is a Windows-first Discord chat control project. One approved Discord user can control the PC by writing natural Korean commands in one configured text channel.

`rev0.0` contains the earlier Discord voice and phone-microphone experiments. `rev0.1` focuses on the simpler and more reliable chat-control path.

## rev0.1 Scope

- The bot reads only one configured Discord text channel.
- Only one configured Discord user can issue control commands.
- The bot ignores messages from other users, other channels, and bots.
- Commands are interpreted from natural Korean chat, not only exact phrases.
- Control mode still gates PC actions:
  - `클로 온`, `클로 켜줘`, `클로 모드 시작해`
  - `클로 오프`, `클로 꺼줘`, `클로 모드 중지해`
- Results are posted back to the configured Discord text channel.
- Risky commands still require confirmation where the core marks them as risky.
- By default, actions run in `dry_run` mode until you explicitly enable Windows control.

## Example Chat

```text
김현종: 클로 켜줘
bot: 클로 모드가 켜졌습니다.

김현종: 브라우저 좀 켜줘
bot: 실행 완료: 브라우저 좀 켜줘

김현종: 계산기 좀 종료해줘
bot: 실행 완료: 계산기 좀 종료해줘

김현종: 다운로드 폴더로 들어가
bot: 이동한 폴더: C:\Users\이안\Downloads
```

## Supported Intent Groups

- Mode: turn OpenClaw control on or off.
- Apps: open or close Notepad, Calculator, Chrome, and File Explorer.
- Folders: show, open, enter, and move up from the current folder. Existing File Explorer windows are reused when possible.
- Mouse: move, position, left click, right click, double click.
- Keyboard: Enter, Escape, common shortcuts, and short text input.
- Confirmation: confirm or cancel pending risky commands.

OpenClaw prefers no action over uncertain action. If a chat message is not understood, it is rejected and logged.

## Configuration

Create `.env` from `.env.example`.

Required for chat control:

```dotenv
DISCORD_BOT_TOKEN=replace-me
DISCORD_GUILD_ID=123456789012345678
DISCORD_OWNER_USER_ID=123456789012345678
DISCORD_TEXT_CHANNEL_ID=123456789012345678
```

Optional voice fields from `rev0.0` can stay empty for `rev0.1`:

```dotenv
DISCORD_VOICE_CHANNEL_ID=
OPENCLAW_ENABLE_VOICE_RECEIVE=false
```

Folder navigation is unrestricted by default. Set this later to keep navigation inside one root folder:

```dotenv
OPENCLAW_SANDBOX_ROOT=C:\Users\이안\Desktop
```

Set real PC control only when you are ready:

```dotenv
OPENCLAW_CONTROLLER_MODE=dry_run
```

Use `OPENCLAW_CONTROLLER_MODE=windows` to perform real Windows app, mouse, and keyboard actions.

Discord Developer Portal must have **Message Content Intent** enabled for the bot, because `rev0.1` reads normal chat messages.

## Running

Check configuration:

```bash
python -m openclaw_discord --check-config
```

Run the Discord chat-control bot:

```bash
python -m openclaw_discord --discord
```

Console mock mode is still available:

```bash
python -m openclaw_discord
```

## Legacy Voice Experiments

The older slash-command, Discord voice receive, and phone-microphone files are preserved from `rev0.0` for reference. They are not needed for `rev0.1` chat control.

## Safety Notes

Never commit Discord bot tokens, user tokens, API keys, or machine-specific secrets.

Risky commands such as file deletion, destructive system changes, payments, credential handling, or arbitrary shell execution are out of scope.
