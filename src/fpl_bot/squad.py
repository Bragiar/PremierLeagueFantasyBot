from __future__ import annotations

import difflib
import math
import unicodedata
from collections import Counter
from typing import Any, Iterable

from fpl_bot.models import OwnedPlayer, Player, POSITION_IDS, POSITION_NAMES, SquadSettings, Transfer


def normalize_name(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_value = "".join(char for char in decomposed if not unicodedata.combining(char))
    return "".join(char.lower() for char in ascii_value if char.isalnum())


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def player_from_api(raw: dict[str, Any], team_names: dict[int, str]) -> Player:
    first = str(raw.get("first_name", "")).strip()
    second = str(raw.get("second_name", "")).strip()
    return Player(
        id=int(raw["id"]),
        name=str(raw.get("web_name") or f"{first} {second}").strip(),
        full_name=f"{first} {second}".strip(),
        position=POSITION_NAMES[int(raw["element_type"])],
        team_id=int(raw["team"]),
        team_name=team_names.get(int(raw["team"]), "Unknown"),
        cost=int(raw["now_cost"]),
        status=str(raw.get("status", "u")),
        chance_next=(
            None
            if raw.get("chance_of_playing_next_round") is None
            else int(raw["chance_of_playing_next_round"])
        ),
        news=str(raw.get("news", "")).strip(),
        can_select=bool(raw.get("can_select", True)),
        minutes=int(raw.get("minutes", 0)),
        starts=int(raw.get("starts", 0)),
        total_points=int(raw.get("total_points", 0)),
        form=_number(raw.get("form")),
        points_per_game=_number(raw.get("points_per_game")),
        selected_by_percent=_number(raw.get("selected_by_percent")),
        expected_next=_number(raw.get("ep_next")),
        defensive_contribution_per_90=_number(
            raw.get("defensive_contribution_per_90")
        ),
        expected_goals=_number(raw.get("expected_goals")),
        expected_assists=_number(raw.get("expected_assists")),
        expected_goal_involvements=_number(raw.get("expected_goal_involvements")),
        expected_goals_conceded=_number(raw.get("expected_goals_conceded")),
        transfers_in_event=int(raw.get("transfers_in_event", 0) or 0),
        transfers_out_event=int(raw.get("transfers_out_event", 0) or 0),
        raw=raw,
    )


def _match_score(query: str, player: Player) -> float:
    normalized_query = normalize_name(query)
    web = normalize_name(player.name)
    full = normalize_name(player.full_name)
    if normalized_query in {web, full}:
        return 2.0

    query_tokens = set(normalize_name(part) for part in query.split())
    full_tokens = set(normalize_name(part) for part in player.full_name.split())
    token_overlap = len(query_tokens.intersection(full_tokens)) / max(1, len(query_tokens))
    sequence = max(
        difflib.SequenceMatcher(None, normalized_query, web).ratio(),
        difflib.SequenceMatcher(None, normalized_query, full).ratio(),
    )
    prefix_bonus = 0.15 if full.startswith(normalized_query) else 0.0
    return sequence + 0.45 * token_overlap + prefix_bonus


def resolve_squad(
    settings: SquadSettings,
    raw_players: Iterable[dict[str, Any]],
    raw_teams: Iterable[dict[str, Any]],
) -> list[OwnedPlayer]:
    team_names = {int(team["id"]): str(team["name"]) for team in raw_teams}
    players = [player_from_api(raw, team_names) for raw in raw_players]
    resolved: list[OwnedPlayer] = []

    for entry in settings.entries:
        positional = [player for player in players if player.position == entry.position]
        ranked = sorted(
            ((_match_score(entry.name, player), player) for player in positional),
            key=lambda item: item[0],
            reverse=True,
        )
        if not ranked or ranked[0][0] < 0.75:
            raise ValueError(f"Could not safely resolve {entry.name!r} in official FPL data")
        if len(ranked) > 1 and ranked[0][0] < 2.0 and ranked[0][0] - ranked[1][0] < 0.08:
            raise ValueError(f"Ambiguous player name {entry.name!r}; use the FPL display name")
        player = ranked[0][1]
        purchase_price = (
            entry.purchase_price
            if entry.purchase_price is not None
            else inferred_initial_purchase_price(player)
        )
        resolved.append(OwnedPlayer(player, purchase_price))

    return resolved


def selling_price(current_price: int, purchase_price: int | None) -> int:
    if purchase_price is None:
        return current_price
    if current_price <= purchase_price:
        return current_price
    return purchase_price + math.floor((current_price - purchase_price) / 2)


def inferred_initial_purchase_price(player: Player) -> int:
    """Recover the season-opening price when an initial squad entry uses null."""
    try:
        change = int(player.raw.get("cost_change_start", 0) or 0)
    except (TypeError, ValueError):
        change = 0
    return max(0, player.cost - change)


def validate_squad(players: Iterable[Player]) -> list[str]:
    squad = list(players)
    errors: list[str] = []
    if len(squad) != 15:
        errors.append(f"Squad has {len(squad)} players; expected 15")
    if len({player.id for player in squad}) != len(squad):
        errors.append("Squad contains duplicate players")

    expected = {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}
    actual = Counter(player.position for player in squad)
    for position, count in expected.items():
        if actual[position] != count:
            errors.append(f"Squad has {actual[position]} {position}; expected {count}")

    for team_id, count in Counter(player.team_id for player in squad).items():
        if count > 3:
            team_name = next(player.team_name for player in squad if player.team_id == team_id)
            errors.append(f"Squad has {count} players from {team_name}; maximum is 3")
    return errors


def apply_and_validate_transfers(
    owned: Iterable[OwnedPlayer], transfers: Iterable[Transfer], bank: int
) -> tuple[list[Player], int, list[str]]:
    current = list(owned)
    available_bank = bank
    errors: list[str] = []

    for transfer in transfers:
        outgoing_index = next(
            (index for index, item in enumerate(current) if item.player.id == transfer.player_out.id),
            None,
        )
        if outgoing_index is None:
            errors.append(f"{transfer.player_out.name} is not in the current squad")
            continue
        outgoing = current[outgoing_index]
        if outgoing.player.position != transfer.player_in.position:
            errors.append(
                f"Position mismatch: {outgoing.player.name} to {transfer.player_in.name}"
            )
            continue
        sale = selling_price(outgoing.player.cost, outgoing.purchase_price)
        if transfer.selling_price != sale:
            errors.append(f"Incorrect selling price for {outgoing.player.name}")
        funds = available_bank + sale
        if transfer.player_in.cost > funds:
            errors.append(
                f"Cannot afford {transfer.player_in.name}: "
                f"£{transfer.player_in.cost / 10:.1f}m costs more than £{funds / 10:.1f}m"
            )
            continue
        available_bank = funds - transfer.player_in.cost
        current[outgoing_index] = OwnedPlayer(transfer.player_in, transfer.player_in.cost)

    proposed = [item.player for item in current]
    errors.extend(validate_squad(proposed))
    return proposed, available_bank, errors


def all_api_players(
    raw_players: Iterable[dict[str, Any]], raw_teams: Iterable[dict[str, Any]]
) -> list[Player]:
    team_names = {int(team["id"]): str(team["name"]) for team in raw_teams}
    return [player_from_api(raw, team_names) for raw in raw_players]
