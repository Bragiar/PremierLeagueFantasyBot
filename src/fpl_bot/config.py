from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from fpl_bot.models import POSITION_IDS, SquadEntry, SquadSettings


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping in {path}")
    return data


def money_to_tenths(value: Any, field_name: str) -> int:
    try:
        return int(round(float(value) * 10))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number in millions") from exc


def load_squad(path: Path) -> SquadSettings:
    data = load_yaml(path)
    raw_entries = data.get("squad")
    if not isinstance(raw_entries, list):
        raise ValueError("data/squad.yaml must contain a squad list")

    entries: list[SquadEntry] = []
    for raw in raw_entries:
        if not isinstance(raw, dict):
            raise ValueError("Every squad entry must be a mapping")
        position = str(raw.get("position", "")).upper()
        if position not in POSITION_IDS:
            raise ValueError(f"Unknown position {position!r}")
        name = str(raw.get("name", "")).strip()
        if not name:
            raise ValueError("Every squad entry needs a name")
        purchase = raw.get("purchase_price")
        entries.append(
            SquadEntry(
                name=name,
                position=position,
                purchase_price=None
                if purchase is None
                else money_to_tenths(purchase, f"purchase_price for {name}"),
            )
        )

    return SquadSettings(
        entries=tuple(entries),
        bank=money_to_tenths(data.get("bank", 0), "bank"),
        free_transfers=max(0, int(data.get("free_transfers", 1))),
        captain=str(data.get("captain", "")).strip(),
        vice_captain=str(data.get("vice_captain", "")).strip(),
    )


def load_strategy(path: Path) -> dict[str, Any]:
    data = load_yaml(path)
    required = {"strategy", "notifications", "openai", "fpl_api"}
    missing = required.difference(data)
    if missing:
        raise ValueError(f"Missing strategy sections: {', '.join(sorted(missing))}")
    return data
