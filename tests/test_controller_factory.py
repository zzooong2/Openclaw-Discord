from openclaw_discord.config import Settings
from openclaw_discord.controller_factory import build_controller
from openclaw_discord.controllers import DryRunController
from openclaw_discord.windows_controller import WindowsController


def make_settings(controller_mode):
    return Settings(
        discord_bot_token="",
        guild_id="",
        owner_user_id="owner",
        voice_channel_id="",
        text_channel_id="",
        log_dir="logs",
        input_block_mode="simulate",
        max_text_input_chars=40,
        controller_mode=controller_mode,
    )


class FakeProcessRunner:
    pass


class FakeInputDriver:
    pass


def test_build_controller_defaults_to_dry_run():
    controller = build_controller(make_settings("dry_run"))

    assert isinstance(controller, DryRunController)


def test_build_controller_can_create_windows_controller_with_injected_dependencies():
    controller = build_controller(
        make_settings("windows"),
        process_runner=FakeProcessRunner(),
        input_driver=FakeInputDriver(),
    )

    assert isinstance(controller, WindowsController)


def test_build_controller_rejects_unknown_mode():
    try:
        build_controller(make_settings("surprise"))
    except ValueError as exc:
        assert str(exc) == "Unsupported controller mode: surprise"
    else:
        raise AssertionError("Expected ValueError")
