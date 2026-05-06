from __future__ import annotations

from dataclasses import dataclass

from openclaw_discord.commands import Command, CommandKind, parse_command
from openclaw_discord.controllers import Controller
from openclaw_discord.logging import LogEvent


@dataclass(frozen=True)
class CommandContext:
    user_id: str


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    status: str
    message: str
    command: Command


class OpenClawCore:
    def __init__(
        self,
        *,
        owner_user_id: str,
        controller: Controller,
        logger: object | None = None,
        input_blocker: object | None = None,
    ) -> None:
        self.owner_user_id = owner_user_id
        self.controller = controller
        self.logger = logger
        self.input_blocker = input_blocker
        self.voice_mode_enabled = False
        self._pending_confirmation: Command | None = None

    def handle_text(self, text: str, context: CommandContext) -> CommandResult:
        command = parse_command(text)
        self._log("voice_command", command.raw_text, {"user_id": context.user_id})
        if context.user_id != self.owner_user_id:
            return self._finish(self._blocked(command, "허용되지 않은 사용자입니다."))

        if command.kind is CommandKind.UNKNOWN:
            return self._finish(self._blocked(command, "알 수 없는 명령입니다."))

        if command.kind is CommandKind.MODE:
            return self._finish(self._handle_mode(command))

        if command.kind is CommandKind.CONFIRMATION:
            return self._finish(self._handle_confirmation(command))

        if not self.voice_mode_enabled:
            return self._finish(self._blocked(command, "클로 모드가 꺼져 있습니다."))

        if command.payload.get("requires_confirmation"):
            self._pending_confirmation = command
            return self._finish(CommandResult(False, "pending_confirmation", f"확인이 필요합니다: {command.raw_text}", command))

        return self._finish(self._execute(command))

    def _handle_mode(self, command: Command) -> CommandResult:
        enabled = bool(command.payload["enabled"])
        self.voice_mode_enabled = enabled
        if self.input_blocker is not None:
            if enabled:
                self.input_blocker.enable()
            else:
                self.input_blocker.disable()
        if not enabled:
            self._pending_confirmation = None
        message = "클로 모드가 켜졌습니다." if enabled else "클로 모드가 꺼졌습니다."
        return CommandResult(True, "success", message, command)

    def _handle_confirmation(self, command: Command) -> CommandResult:
        if command.action == "cancel":
            self._pending_confirmation = None
            return CommandResult(True, "success", "대기 중인 명령을 취소했습니다.", command)

        if self._pending_confirmation is None:
            return self._blocked(command, "확인할 명령이 없습니다.")

        pending = self._pending_confirmation
        self._pending_confirmation = None
        return self._execute(pending)

    def _execute(self, command: Command) -> CommandResult:
        detail = self.controller.execute(command)
        message = detail or f"실행 완료: {command.raw_text}"
        return CommandResult(True, "success", message, command)

    @staticmethod
    def _blocked(command: Command, reason: str) -> CommandResult:
        return CommandResult(False, "blocked", f"차단: {reason}", command)

    def _finish(self, result: CommandResult) -> CommandResult:
        event_type = result.status if result.status in {"success", "blocked", "failure"} else "blocked"
        self._log(event_type, result.message, {"command": result.command.raw_text})
        return result

    def _log(self, event_type: str, message: str, details: dict[str, object]) -> None:
        if self.logger is not None:
            self.logger.write(LogEvent(event_type, message, details))
