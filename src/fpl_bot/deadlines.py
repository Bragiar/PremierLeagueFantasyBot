from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Iterable

from fpl_bot.models import Event


WINDOW_LABELS = {1440: "24h", 180: "3h", 45: "45m"}


def parse_fpl_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def event_from_dict(raw: dict[str, Any]) -> Event:
    return Event(
        id=int(raw["id"]),
        name=str(raw.get("name") or f"Gameweek {raw['id']}"),
        deadline=parse_fpl_datetime(str(raw["deadline_time"])),
    )


def select_next_event(events: Iterable[dict[str, Any]], now: datetime) -> Event | None:
    now = now.astimezone(UTC)
    future: list[Event] = []
    for raw in events:
        deadline = raw.get("deadline_time")
        if not deadline:
            continue
        event = event_from_dict(raw)
        if event.deadline > now and not raw.get("finished", False):
            future.append(event)
    return min(future, key=lambda event: event.deadline, default=None)


def due_window(
    deadline: datetime,
    now: datetime,
    offsets_minutes: Iterable[int],
    tolerance_minutes: int,
) -> str | None:
    minutes_remaining = (deadline - now).total_seconds() / 60
    if minutes_remaining <= 0:
        return None
    for offset in sorted((int(value) for value in offsets_minutes), reverse=True):
        if offset - tolerance_minutes < minutes_remaining <= offset:
            return WINDOW_LABELS.get(offset, f"{offset}m")
    return None


def notification_key(event_id: int, window: str) -> str:
    return f"gw{event_id}:{window}"


def serialize_future_events(
    events: Iterable[dict[str, Any]], now: datetime, limit: int = 8
) -> list[dict[str, Any]]:
    future: list[Event] = []
    for raw in events:
        try:
            event = event_from_dict(raw)
        except (KeyError, TypeError, ValueError):
            continue
        if event.deadline > now.astimezone(UTC):
            future.append(event)
    future.sort(key=lambda event: event.deadline)
    return [
        {
            "id": event.id,
            "name": event.name,
            "deadline_time": event.deadline.isoformat().replace("+00:00", "Z"),
            "finished": False,
        }
        for event in future[:limit]
    ]
