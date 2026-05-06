# Environment Variables

All runtime configuration is stored in `.env`. Do not commit a real `.env` file containing secrets.

## Required

Discord server invite for reference: `https://discord.gg/VGySqE2y`

| Variable | Description |
| --- | --- |
| `DISCORD_BOT_TOKEN` | Discord bot token |
| `DISCORD_GUILD_ID` | Discord server ID where slash commands and voice control are allowed |
| `DISCORD_OWNER_USER_ID` | Only this Discord user can issue control commands |
| `DISCORD_VOICE_CHANNEL_ID` | Only this voice channel is allowed for voice control |
| `DISCORD_TEXT_CHANNEL_ID` | Text channel where command results are posted |

## Runtime Behavior

| Variable | Default | Description |
| --- | --- | --- |
| `OPENCLAW_INPUT_BLOCK_MODE` | `simulate` | `simulate` logs blocked input; `real` blocks keyboard and mouse input |
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
DISCORD_VOICE_CHANNEL_ID=123456789012345678
DISCORD_TEXT_CHANNEL_ID=123456789012345678

OPENCLAW_INPUT_BLOCK_MODE=simulate
OPENCLAW_LOG_DIR=logs
OPENCLAW_MOUSE_STEP=120
OPENCLAW_MOUSE_SMALL_STEP=30
OPENCLAW_MAX_TEXT_INPUT_CHARS=40
```
