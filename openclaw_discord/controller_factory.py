from __future__ import annotations

from openclaw_discord.config import Settings
from openclaw_discord.controllers import Controller, DryRunController
from openclaw_discord.windows_controller import (
    InputDriver,
    ProcessRunner,
    PyAutoGuiInputDriver,
    SubprocessRunner,
    WindowsController,
)


def build_controller(
    settings: Settings,
    *,
    process_runner: ProcessRunner | None = None,
    input_driver: InputDriver | None = None,
) -> Controller:
    if settings.controller_mode == "dry_run":
        return DryRunController()

    if settings.controller_mode == "windows":
        return WindowsController(
            process_runner=process_runner or SubprocessRunner(),
            input_driver=input_driver or PyAutoGuiInputDriver(),
        )

    raise ValueError(f"Unsupported controller mode: {settings.controller_mode}")

