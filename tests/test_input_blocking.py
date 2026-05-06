from openclaw_discord.input_blocking import InputBlockEvent, SimulatedInputBlocker


def test_simulated_blocker_records_keyboard_event_when_enabled():
    blocker = SimulatedInputBlocker()

    blocker.enable()
    blocked = blocker.record_event(InputBlockEvent("keyboard", "a"))

    assert blocked is True
    assert blocker.events == [InputBlockEvent("keyboard", "a")]


def test_simulated_blocker_does_not_record_when_disabled():
    blocker = SimulatedInputBlocker()

    blocked = blocker.record_event(InputBlockEvent("mouse", "left_click"))

    assert blocked is False
    assert blocker.events == []


def test_emergency_hotkey_is_never_blocked():
    blocker = SimulatedInputBlocker()

    blocker.enable()
    blocked = blocker.record_event(InputBlockEvent("keyboard", "ctrl+alt+f12"))

    assert blocked is False
    assert blocker.events == []


def test_disable_clears_enabled_state_but_keeps_audit_events():
    blocker = SimulatedInputBlocker()

    blocker.enable()
    blocker.record_event(InputBlockEvent("keyboard", "a"))
    blocker.disable()
    blocked = blocker.record_event(InputBlockEvent("keyboard", "b"))

    assert blocker.enabled is False
    assert blocked is False
    assert blocker.events == [InputBlockEvent("keyboard", "a")]

