from datetime import UTC, datetime, timedelta

from fpl_bot.deadlines import due_window


def test_deadline_windows_are_detected_after_each_threshold():
    deadline = datetime(2026, 8, 28, 17, 30, tzinfo=UTC)

    assert due_window(deadline, deadline - timedelta(hours=24), [1440, 180, 45], 40) == "24h"
    assert due_window(deadline, deadline - timedelta(minutes=1420), [1440, 180, 45], 40) == "24h"
    assert due_window(deadline, deadline - timedelta(hours=3), [1440, 180, 45], 40) == "3h"
    assert due_window(deadline, deadline - timedelta(minutes=45), [1440, 180, 45], 40) == "45m"


def test_delayed_runs_remain_due_until_the_next_threshold():
    deadline = datetime(2026, 8, 28, 17, 30, tzinfo=UTC)

    assert due_window(deadline, deadline - timedelta(minutes=1399), [1440, 180, 45], 40) == "24h"
    assert due_window(deadline, deadline - timedelta(minutes=120), [1440, 180, 45], 40) == "3h"
    assert due_window(deadline, deadline - timedelta(minutes=10), [1440, 180, 45], 40) == "45m"
    assert due_window(deadline, deadline - timedelta(minutes=1441), [1440, 180, 45], 40) is None
    assert due_window(deadline, deadline + timedelta(seconds=1), [1440, 180, 45], 40) is None
