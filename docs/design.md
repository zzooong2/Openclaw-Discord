# OpenClaw Discord Design

## Goal

Build a Discord-connected Windows PC controller that accepts fixed Korean voice commands from one approved user, executes only allowed actions, and keeps strong mode, logging, and emergency-off boundaries.

## High-Level Flow

```text
Discord voice channel
  -> Speech input adapter
  -> Fixed Korean command parser
  -> Permission, mode, confirmation, and safety gate
  -> OpenClaw Core
  -> Windows controller adapter
  -> Discord text feedback and logs
```

## Core Decisions

- OpenClaw is not an external dependency. It is the project-owned PC-control core.
- STT is not selected yet. The code should expose a speech input interface so console mock input, Discord voice input, and a future STT engine can be swapped.
- Commands are fixed Korean phrases only for MVP.
- Command aliases are disabled for MVP.
- The project targets the developer's Windows PC first.
- All runtime configuration uses `.env`.
- Discord feedback goes to one configured text channel.

## Components

### Discord Gateway

Owns Discord connection, slash commands, voice-channel joining/leaving, voice event routing, and text-channel responses.

Required slash commands:

- `/join`
- `/leave`
- `/voice-mode off`

The gateway must reject commands from users other than the configured owner.

### Speech Input Adapter

Produces recognized text strings for the command pipeline.

Initial adapters:

- Console mock adapter for local development.
- Discord voice adapter with a placeholder STT boundary.

Future STT engines should be added behind this interface instead of changing command execution code.

### Command Parser

Converts exact Korean command text into structured command objects.

Examples:

- `클로 온` -> `mode.set(enabled=True)`
- `클로 오프` -> `mode.set(enabled=False)`
- `메모장 열어` -> `app.open(target="notepad")`
- `왼쪽 클릭` -> `mouse.click(button="left")`

Unknown text must produce a rejected parse result, not a guessed command.

### Safety Gate

Checks whether a parsed command is allowed.

Rules:

- Only the configured Discord owner can issue commands.
- When voice control mode is off, only mode-on commands and emergency-off commands are allowed.
- Destructive or risky commands are not implemented in MVP.
- Selected commands such as app close or window close require confirmation.
- Emergency off commands are always allowed.

### OpenClaw Core

Owns system state and command orchestration.

State:

- Voice control mode: on/off.
- Pending confirmation command, if any.
- Input-blocking mode: simulation until all emergency-off paths pass verification, then real blocking.

Responsibilities:

- Route valid commands to the correct controller adapter.
- Refuse invalid commands with a short user-facing reason.
- Emit structured log events for voice commands, successes, failures, and blocked actions.
- Send concise Discord text feedback.

### Windows Controller Adapter

Executes allowed PC operations.

MVP operations:

- Open/close configured basic apps: Notepad, Calculator, Chrome, File Explorer.
- Move mouse by relative offsets.
- Move mouse to known screen positions.
- Left click, right click, double click.
- Send shortcuts.
- Type short text.

The first implementation should use Python libraries. Windows API calls should be introduced only when library behavior is insufficient.

### Input Blocking

Input blocking starts in simulation mode. In simulation mode, physical keyboard and mouse events that would be blocked are logged, but not actually blocked.

Real blocking is added only after emergency-off paths are working:

- `Ctrl + Alt + F12`
- `/voice-mode off`
- `클로 오프`

## Logging

The system stores both JSONL and human-readable text logs.

JSONL event types:

- `voice_command`
- `success`
- `failure`
- `blocked`

Text logs should use clear tags such as:

- `[VOICE]`
- `[OK]`
- `[FAIL]`
- `[BLOCKED]`

The user-facing Discord message should be short. Detailed exception or environment information belongs in logs.

## Error Handling

- Unknown command: reject and log as `blocked`.
- Unauthorized user: reject and log as `blocked`.
- Mode off with PC-control command: reject and log as `blocked`.
- Controller execution error: report short failure in Discord and log detailed failure.
- Emergency off: immediately set voice control mode off and disable real input blocking if active.

## Testing Strategy

Use `pytest` first for behavior that can be tested without Discord or real PC input:

- Fixed command parsing.
- Mode gating.
- Owner-only permission checks.
- Confirmation flow.
- Log event formatting.
- Controller adapter calls through fakes.

Integration testing for Discord voice and real input blocking comes after the core behavior is stable.
