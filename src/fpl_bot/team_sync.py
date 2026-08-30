from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from fpl_bot.auth import (
    ENTRY_ID_ACCOUNT,
    REFRESH_TOKEN_ACCOUNT,
    FPLAuthError,
    KeychainStore,
    authenticated_get,
    refresh_access_token,
    stored_entry_id,
    stored_refresh_token,
)
from fpl_bot.models import POSITION_NAMES
from fpl_bot.storage import append_jsonl, atomic_write_text


API_BASE = "https://fantasy.premierleague.com/api"
CHIP_NAMES = {
    "wildcard": "wildcard",
    "freehit": "free_hit",
    "free_hit": "free_hit",
    "bboost": "bench_boost",
    "bench_boost": "bench_boost",
    "3xc": "triple_captain",
    "triple_captain": "triple_captain",
}


@dataclass(frozen=True)
class SyncResult:
    changed: bool
    message: str
    changed_fields: tuple[str, ...] = ()


def _integer(value: Any, field: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Authenticated FPL response has invalid {field}") from exc


def _current_event(bootstrap: dict[str, Any]) -> int:
    events = bootstrap.get("events")
    if not isinstance(events, list):
        raise ValueError("FPL bootstrap response has no events")
    next_event = next((event for event in events if event.get("is_next")), None)
    current = next_event or next((event for event in events if event.get("is_current")), None)
    if not isinstance(current, dict):
        raise ValueError("FPL bootstrap response has no current or next event")
    return _integer(current.get("id"), "event ID")


def _available_free_transfers(transfers: dict[str, Any]) -> int:
    limit = _integer(transfers.get("limit"), "transfer limit")
    made = _integer(transfers.get("made", 0), "transfers made")
    return max(0, limit - made)


def _chip_state(
    previous: dict[str, Any], chips: Any, event_id: int
) -> dict[str, dict[str, str]]:
    raw_previous = previous.get("chips")
    result: dict[str, dict[str, str]] = {
        half: dict(values) if isinstance(values, dict) else {}
        for half, values in (
            raw_previous.items() if isinstance(raw_previous, dict) else []
        )
    }
    for half in ("first_half", "second_half"):
        result.setdefault(half, {})
        for chip in CHIP_NAMES.values():
            result[half].setdefault(chip, "used")

    if not isinstance(chips, list):
        return result
    current_half = "first_half" if event_id <= 19 else "second_half"
    for raw in chips:
        if not isinstance(raw, dict):
            continue
        key = CHIP_NAMES.get(str(raw.get("name", "")).lower())
        status = str(raw.get("status", "")).lower()
        if key and status in {"available", "used"}:
            result[current_half][key] = status
    return result


def build_synced_settings(
    previous: dict[str, Any],
    my_team: dict[str, Any],
    bootstrap: dict[str, Any],
    *,
    entry_id: int,
    confirmed_at: datetime,
) -> dict[str, Any]:
    picks = my_team.get("picks")
    transfers = my_team.get("transfers")
    elements = bootstrap.get("elements")
    if not isinstance(picks, list) or len(picks) != 15:
        raise ValueError("Authenticated FPL team must contain exactly 15 picks")
    if not isinstance(transfers, dict):
        raise ValueError("Authenticated FPL response has no transfer state")
    if not isinstance(elements, list):
        raise ValueError("FPL bootstrap response has no players")

    players = {
        _integer(raw.get("id"), "player ID"): raw
        for raw in elements
        if isinstance(raw, dict)
    }
    squad: list[dict[str, Any]] = []
    captain = ""
    vice_captain = ""
    club_counts: Counter[int] = Counter()
    position_counts: Counter[str] = Counter()

    for pick in picks:
        if not isinstance(pick, dict):
            raise ValueError("Authenticated FPL pick is not an object")
        player_id = _integer(pick.get("element"), "pick player ID")
        player = players.get(player_id)
        if player is None:
            raise ValueError(f"Authenticated FPL pick references unknown player {player_id}")
        position = POSITION_NAMES.get(_integer(player.get("element_type"), "position"))
        if position is None:
            raise ValueError(f"Player {player_id} has an unknown position")
        name = str(player.get("web_name") or "").strip()
        if not name:
            raise ValueError(f"Player {player_id} has no display name")
        purchase_price = _integer(pick.get("purchase_price"), "purchase price")
        squad.append(
            {
                "name": name,
                "position": position,
                "purchase_price": purchase_price / 10,
            }
        )
        club_counts[_integer(player.get("team"), "team ID")] += 1
        position_counts[position] += 1
        if pick.get("is_captain"):
            captain = name
        if pick.get("is_vice_captain"):
            vice_captain = name

    expected_positions = Counter({"GK": 2, "DEF": 5, "MID": 5, "FWD": 3})
    if position_counts != expected_positions:
        raise ValueError(f"Authenticated FPL squad has invalid positions: {position_counts}")
    if any(count > 3 for count in club_counts.values()):
        raise ValueError("Authenticated FPL squad exceeds the three-player club limit")
    if not captain or not vice_captain or captain == vice_captain:
        raise ValueError("Authenticated FPL captain and vice-captain are invalid")

    event_id = _current_event(bootstrap)
    return {
        "fpl_entry_id": entry_id,
        "last_confirmed_at": confirmed_at.astimezone(UTC).isoformat(),
        "bank": _integer(transfers.get("bank"), "bank") / 10,
        "free_transfers": _available_free_transfers(transfers),
        "captain": captain,
        "vice_captain": vice_captain,
        "chips": _chip_state(previous, my_team.get("chips"), event_id),
        "squad": squad,
    }


def _flow_mapping(value: dict[str, Any]) -> str:
    rendered = yaml.safe_dump(
        value,
        allow_unicode=True,
        default_flow_style=True,
        sort_keys=False,
        width=1000,
    ).strip()
    return rendered


def render_squad_yaml(settings: dict[str, Any]) -> str:
    lines = [
        "# Automatically synchronized from the authenticated, read-only FPL team endpoint.",
        "# Purchase prices come from FPL's own-team response and are required for selling value.",
        "# Never place FPL credentials or tokens in this file.",
        f"fpl_entry_id: {int(settings['fpl_entry_id'])}",
        f"last_confirmed_at: {json.dumps(settings['last_confirmed_at'])}",
        f"bank: {float(settings['bank']):.1f}",
        f"free_transfers: {int(settings['free_transfers'])}",
        f"captain: {settings['captain']}",
        f"vice_captain: {settings['vice_captain']}",
        "chips:",
    ]
    for half in ("first_half", "second_half"):
        lines.append(f"  {half}:")
        for chip in ("wildcard", "free_hit", "bench_boost", "triple_captain"):
            lines.append(f"    {chip}: {settings['chips'][half][chip]}")
    lines.append("squad:")
    for entry in settings["squad"]:
        lines.append(f"  - {_flow_mapping(entry)}")
    return "\n".join(lines) + "\n"


def _material_view(settings: dict[str, Any]) -> dict[str, Any]:
    return {
        key: settings.get(key)
        for key in (
            "bank",
            "free_transfers",
            "captain",
            "vice_captain",
            "chips",
            "squad",
        )
    }


def _changed_fields(previous: dict[str, Any], current: dict[str, Any]) -> tuple[str, ...]:
    before = _material_view(previous)
    after = _material_view(current)
    return tuple(key for key in after if before.get(key) != after.get(key))


def _transfer_record(
    previous: dict[str, Any], current: dict[str, Any], confirmed_at: datetime
) -> dict[str, Any] | None:
    old_entries = {
        str(item.get("name")): item
        for item in previous.get("squad", [])
        if isinstance(item, dict)
    }
    new_entries = {
        str(item.get("name")): item
        for item in current.get("squad", [])
        if isinstance(item, dict)
    }
    sold = [old_entries[name] for name in sorted(old_entries.keys() - new_entries)]
    bought = [new_entries[name] for name in sorted(new_entries.keys() - old_entries)]
    if not sold and not bought:
        return None
    return {
        "schema_version": 1,
        "confirmed_at": confirmed_at.astimezone(UTC).isoformat(),
        "entry_id": current["fpl_entry_id"],
        "sold": sold,
        "bought": bought,
        "bank_after": current["bank"],
        "free_transfers_after": current["free_transfers"],
        "source": "authenticated_fpl_sync",
    }


def sync_team(repo_root: Path, *, now: datetime | None = None) -> SyncResult:
    confirmed_at = (now or datetime.now(UTC)).astimezone(UTC)
    store = KeychainStore()
    entry_id = stored_entry_id(store)
    refresh_token = stored_refresh_token(store)
    tokens = refresh_access_token(refresh_token)
    # Persist rotation before the authenticated request so a later API failure does not
    # discard the newest usable refresh token.
    store.set(REFRESH_TOKEN_ACCOUNT, tokens.refresh_token)

    my_team = authenticated_get(
        f"{API_BASE}/my-team/{entry_id}/", tokens.access_token
    )
    bootstrap = authenticated_get(f"{API_BASE}/bootstrap-static/", tokens.access_token)
    if not isinstance(my_team, dict) or not isinstance(bootstrap, dict):
        raise ValueError("FPL synchronization responses are not JSON objects")

    squad_path = repo_root / "data" / "squad.yaml"
    with squad_path.open("r", encoding="utf-8") as handle:
        previous = yaml.safe_load(handle)
    if not isinstance(previous, dict):
        raise ValueError("data/squad.yaml must contain a YAML mapping")

    current = build_synced_settings(
        previous,
        my_team,
        bootstrap,
        entry_id=entry_id,
        confirmed_at=confirmed_at,
    )
    fields = _changed_fields(previous, current)
    if not fields:
        return SyncResult(False, "Authenticated FPL squad already matches data/squad.yaml")

    history = _transfer_record(previous, current, confirmed_at)
    atomic_write_text(squad_path, render_squad_yaml(current))
    if history is not None:
        append_jsonl(repo_root / "logs" / "actual_transfer_history.jsonl", history)
    return SyncResult(
        True,
        "Synchronized authenticated FPL team: " + ", ".join(fields),
        fields,
    )


def configure_auth(entry_id: int, refresh_token: str) -> None:
    if entry_id <= 0:
        raise ValueError("FPL entry ID must be positive")
    if not refresh_token.strip():
        raise ValueError("FPL refresh token cannot be empty")
    store = KeychainStore()
    store.set(ENTRY_ID_ACCOUNT, str(entry_id))
    store.set(REFRESH_TOKEN_ACCOUNT, refresh_token.strip())
    tokens = refresh_access_token(refresh_token.strip())
    store.set(REFRESH_TOKEN_ACCOUNT, tokens.refresh_token)
    value = authenticated_get(f"{API_BASE}/my-team/{entry_id}/", tokens.access_token)
    if not isinstance(value, dict) or not isinstance(value.get("picks"), list):
        raise FPLAuthError("FPL authorization succeeded but the team response was invalid")
