import json

from openclaw_discord.logging import LogEvent, OpenClawLogger


def test_writes_jsonl_log_event(tmp_path):
    logger = OpenClawLogger(tmp_path)

    logger.write(LogEvent("voice_command", "클로 온", {"user_id": "owner-1"}))

    lines = (tmp_path / "openclaw.jsonl").read_text(encoding="utf-8").splitlines()
    event = json.loads(lines[0])
    assert event["type"] == "voice_command"
    assert event["message"] == "클로 온"
    assert event["details"] == {"user_id": "owner-1"}
    assert "timestamp" in event


def test_writes_text_log_tags(tmp_path):
    logger = OpenClawLogger(tmp_path)

    logger.write(LogEvent("voice_command", "클로 온"))
    logger.write(LogEvent("success", "클로 모드가 켜졌습니다."))
    logger.write(LogEvent("failure", "실패: 실행 오류"))
    logger.write(LogEvent("blocked", "차단: 알 수 없는 명령입니다."))

    text = (tmp_path / "openclaw.log").read_text(encoding="utf-8")
    assert "[VOICE] 클로 온" in text
    assert "[OK] 클로 모드가 켜졌습니다." in text
    assert "[FAIL] 실패: 실행 오류" in text
    assert "[BLOCKED] 차단: 알 수 없는 명령입니다." in text

