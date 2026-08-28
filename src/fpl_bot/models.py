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
    chips: dict[str, dict[str, str]] = field(default_factory=dict)


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


@dataclass(frozen=True)
class EngineOption:
    id: str
    action: str
    projected_gain: float
    rationale: str
    transfer: Transfer | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "action": self.action,
            "projected_gain": round(self.projected_gain, 2),
            "rationale": self.rationale,
            "transfer": None if self.transfer is None else self.transfer.to_dict(),
        }


@dataclass(frozen=True)
class ChipOption:
    id: str
    chip: str
    projected_uplift: float
    rationale: str
    squad: tuple[Player, ...] = field(default=(), repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "chip": self.chip,
            "projected_uplift": round(self.projected_uplift, 2),
            "rationale": self.rationale,
            "squad": [
                {
                    "id": player.id,
                    "name": player.name,
                    "position": player.position,
                    "team": player.team_name,
                    "cost": player.cost / 10,
                }
                for player in self.squad
            ],
        }


@dataclass(frozen=True)
class ResearchSource:
    title: str
    url: str
    date: str


@dataclass(frozen=True)
class ResearchReview:
    verdict: str
    confidence: str
    recommended_option_id: str
    summary: str
    risks: tuple[str, ...]
    sources: tuple[ResearchSource, ...]
    recommended_chip_id: str = "chip:none"
    changed_engine_choice: bool = False
    changed_chip_choice: bool = False


@dataclass(frozen=True)
class PlannedMove:
    player_out_id: int
    player_out: str
    player_in_id: int
    player_in: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GameweekPlan:
    event_id: int
    event_name: str
    transfers: tuple[PlannedMove, ...]
    chip: str
    captain: str
    starting_xi: tuple[str, ...]
    bench: tuple[str, ...]
    reserve_goalkeeper: str
    projected_score: float
    points_hit: int
    free_transfers_before: int
    free_transfers_after: int
    bank_after: float
    confidence: str
    rationale: str

    @property
    def action(self) -> str:
        if not self.transfers:
            return "Roll / no transfer"
        return ", ".join(
            f"{move.player_out} → {move.player_in}" for move in self.transfers
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["transfers"] = [move.to_dict() for move in self.transfers]
        data["action"] = self.action
        return data


@dataclass(frozen=True)
class ChipTarget:
    chip_id: str
    chip: str
    primary_event_id: int | None
    primary_event_name: str
    backup_event_id: int | None
    backup_event_name: str
    target_player: str | None
    projected_uplift: float
    confidence: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RollingPlan:
    generated_for_event: int
    horizon: int
    total_projected_score: float
    gameweeks: tuple[GameweekPlan, ...]
    chip_targets: tuple[ChipTarget, ...]
    changes: tuple[str, ...] = ()
    methodology: str = (
        "Bounded rolling-horizon search using current prices and projections; "
        "future actions are provisional and recalculated every run."
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_for_event": self.generated_for_event,
            "horizon": self.horizon,
            "total_projected_score": round(self.total_projected_score, 2),
            "gameweeks": [week.to_dict() for week in self.gameweeks],
            "chip_targets": [target.to_dict() for target in self.chip_targets],
            "changes": list(self.changes),
            "methodology": self.methodology,
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
    selected_option_id: str = "hold"
    engine_options: list[EngineOption] = field(default_factory=list)
    selected_chip_id: str = "chip:none"
    chip_options: list[ChipOption] = field(default_factory=list)
    research_review: ResearchReview | None = None
    rolling_plan: RollingPlan | None = None
    validation: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["event"] = {
            "id": self.event.id,
            "name": self.event.name,
            "deadline": self.event.deadline.isoformat(),
        }
        data["transfers"] = [transfer.to_dict() for transfer in self.transfers]
        data["engine_options"] = [option.to_dict() for option in self.engine_options]
        data["chip_options"] = [option.to_dict() for option in self.chip_options]
        data["rolling_plan"] = (
            None if self.rolling_plan is None else self.rolling_plan.to_dict()
        )
        return data
