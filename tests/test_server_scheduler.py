from datetime import UTC, datetime, timedelta
import pytest

from fpl_bot.server_scheduler import next_wakeup


NOW = datetime(2026, 10, 18, 10, tzinfo=UTC)


def event(number, minutes):
    return {"id": number, "deadline_time": (NOW + timedelta(minutes=minutes)).isoformat()}


def test_schedules_exactly_two_hours_before_next_deadline():
    assert next_wakeup([event(9, 600), event(8, 300)], {}, NOW) == (NOW + timedelta(minutes=180), 8)


def test_successful_delivery_skips_to_following_gameweek():
    state = {"sent_notifications": {"gw8:120m": NOW.isoformat()}}
    assert next_wakeup([event(8, 100), event(9, 10000)], state, NOW)[1] == 9


def test_late_start_catches_up_but_does_not_schedule_past_deadline():
    assert next_wakeup([event(8, 90)], {}, NOW) == (NOW + timedelta(seconds=15), 8)
    assert next_wakeup([event(8, 10)], {}, NOW) is None
    assert next_wakeup([event(8, -1)], {}, NOW) is None


def test_failed_delivery_remains_eligible_for_retry():
    state = {"sent_notifications": {}, "last_run": {"delivery": "failed"}}
    assert next_wakeup([event(8, 90)], state, NOW)[1] == 8
