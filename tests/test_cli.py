import pytest

from openclaw_discord.__main__ import build_parser


def test_cli_help_exits_cleanly(capsys):
    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--help"])

    assert exc_info.value.code == 0
    assert "OpenClaw Discord console mock" in capsys.readouterr().out


def test_cli_accepts_discord_mode_flag():
    parser = build_parser()

    args = parser.parse_args(["--discord"])

    assert args.discord is True
