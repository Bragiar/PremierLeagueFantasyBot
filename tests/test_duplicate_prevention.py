from fpl_bot.deadlines import notification_key
from fpl_bot.service import already_notified


def test_notification_key_is_per_gameweek_and_window():
    state = {"sent_notifications": {"gw4:3h": "2026-09-12T09:30:00+00:00"}}

    assert already_notified(state, notification_key(4, "3h"))
    assert not already_notified(state, notification_key(4, "45m"))
    assert not already_notified(state, notification_key(5, "3h"))


def test_missing_or_malformed_sent_state_is_safe():
    assert not already_notified({}, "gw1:24h")
    assert not already_notified({"sent_notifications": []}, "gw1:24h")
