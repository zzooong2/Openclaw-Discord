# Environment Variables

All runtime configuration is stored in `.env`. Do not commit a real `.env` file containing secrets.

## Required

Discord server invite for reference: `https://discord.gg/VGySqE2y`

| Variable | Description |
| --- | --- |
| `DISCORD_BOT_TOKEN` | Discord bot token |
| `DISCORD_GUILD_ID` | Discord server ID where chat control is allowed |
| `DISCORD_OWNER_USER_ID` | Only this Discord user can issue control commands |
| `DISCORD_TEXT_CHANNEL_ID` | Only this text channel is read for commands and command results are posted there |

## Runtime Behavior

| Variable | Default | Description |
| --- | --- | --- |
| `OPENCLAW_INPUT_BLOCK_MODE` | `simulate` | `simulate` logs blocked input; `real` blocks keyboard and mouse input |
| `OPENCLAW_CONTROLLER_MODE` | `dry_run` | `dry_run` logs actions; `windows` performs Windows app, mouse, and keyboard actions |
| `OPENCLAW_ENABLE_VOICE_RECEIVE` | `false` | `true` enables experimental Discord voice receive and STT sink wiring |
| `DISCORD_VOICE_CHANNEL_ID` | empty | Optional. Required only when `OPENCLAW_ENABLE_VOICE_RECEIVE=true` or `/join` is used |
| `OPENCLAW_LOG_DIR` | `logs` | Directory for text and JSONL logs |
| `OPENCLAW_MOUSE_STEP` | `120` | Default relative mouse movement in pixels |
| `OPENCLAW_MOUSE_SMALL_STEP` | `30` | Small relative mouse movement in pixels |
| `OPENCLAW_MAX_TEXT_INPUT_CHARS` | `40` | Maximum length for spoken text input |

## Future STT

These are intentionally not required for the first documentation-only commit. They can be added when an STT engine is selected.

| Variable | Description |
| --- | --- |
| `OPENCLAW_STT_PROVIDER` | Future STT provider selection |
| `OPENAI_API_KEY` | Future OpenAI-backed STT key, if selected |

## Example

```dotenv
DISCORD_BOT_TOKEN=replace-me
DISCORD_GUILD_ID=123456789012345678
DISCORD_OWNER_USER_ID=123456789012345678
DISCORD_TEXT_CHANNEL_ID=123456789012345678
DISCORD_VOICE_CHANNEL_ID=

OPENCLAW_INPUT_BLOCK_MODE=simulate
OPENCLAW_LOG_DIR=logs
OPENCLAW_MOUSE_STEP=120
OPENCLAW_MOUSE_SMALL_STEP=30
OPENCLAW_MAX_TEXT_INPUT_CHARS=40
```
