from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


POSITION_IDS = {"GK": 1, "DEF": 2, "MID": 3, "FWD": 4}
POSITION_NAMES = {value: key for key, value in POSITION_IDS.items()}


@dataclass(frozen=True)
class SquadEntry:
    name: str
    position: str
    purchase_price: int | None = None


@dataclass(frozen=True)
class SquadSettings:
    entries: tuple[SquadEntry, ...]
    bank: int
    free_transfers: int
    captain: str
    vice_captain: str


@dataclass(frozen=True)
class Player:
    id: int
    name: str
    full_name: str
    position: str
    team_id: int
    team_name: str
    cost: int
    status: str
    chance_next: int | None
    news: str
    can_select: bool
    minutes: int
    starts: int
    total_points: int
    form: float
    points_per_game: float
    selected_by_percent: float
    expected_next: float
    defensive_contribution_per_90: float
    raw: dict[str, Any] = field(repr=False, compare=False)


@dataclass(frozen=True)
class OwnedPlayer:
    player: Player
    purchase_price: int | None


@dataclass(frozen=True)
class Event:
    id: int
    name: str
    deadline: datetime


@dataclass(frozen=True)
class Transfer:
    player_out: Player
    player_in: Player
    selling_price: int
    buying_price: int
    points_hit: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "out": self.player_out.name,
            "out_id": self.player_out.id,
            "in": self.player_in.name,
            "in_id": self.player_in.id,
            "selling_price": self.selling_price / 10,
            "buying_price": self.buying_price / 10,
            "points_hit": self.points_hit,
        }


@dataclass
class Recommendation:
    event: Event
    transfers: list[Transfer]
    points_hit: int
    captain: str
    vice_captain: str
    starting_xi: list[str]
    bench: list[str]
    reserve_goalkeeper: str
    chip: str
    confidence: str
    explanation: str
    source: str = "deterministic"
    fallback: bool = False
    ai_commentary: str | None = None
    validation: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["event"] = {
            "id": self.event.id,
            "name": self.event.name,
            "deadline": self.event.deadline.isoformat(),
        }
        data["transfers"] = [transfer.to_dict() for transfer in self.transfers]
        return data
