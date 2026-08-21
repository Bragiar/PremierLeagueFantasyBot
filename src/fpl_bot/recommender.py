from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from fpl_bot.models import Event, OwnedPlayer, Player, Recommendation, SquadSettings, Transfer
from fpl_bot.squad import (
    all_api_players,
    apply_and_validate_transfers,
    normalize_name,
    selling_price,
    validate_squad,
)


def availability(player: Player) -> int:
    if not player.can_select or player.status in {"i", "s", "u"}:
        return 0
    if player.chance_next is not None:
        return max(0, min(100, player.chance_next))
    return 100 if player.status == "a" else 75


def fixture_difficulties(
    fixtures: Iterable[dict[str, Any]], event_id: int, horizon: int
) -> dict[int, list[int]]:
    result: dict[int, list[int]] = defaultdict(list)
    last_event = event_id + horizon - 1
    for fixture in fixtures:
        fixture_event = fixture.get("event")
        if fixture_event is None or not event_id <= int(fixture_event) <= last_event:
            continue
        if fixture.get("finished", False):
            continue
        home = int(fixture["team_h"])
        away = int(fixture["team_a"])
        result[home].append(int(fixture.get("team_h_difficulty") or 3))
        result[away].append(int(fixture.get("team_a_difficulty") or 3))
    return result


def score_player(
    player: Player,
    difficulties: list[int],
    strategy: dict[str, Any],
) -> float:
    games = max(1, len(difficulties))
    expected = max(player.expected_next, player.points_per_game, player.form, 2.0)
    base = expected * games
    fixture_edge = sum(3.2 - difficulty for difficulty in difficulties)

    if player.minutes > 0:
        secure_starter = min(1.0, player.starts * 75 / max(1, player.minutes))
    else:
        # Before Gameweek 1, ownership and official availability are the safest
        # public proxies for role security.
        secure_starter = min(1.0, 0.7 + player.selected_by_percent / 200)

    score = (
        base
        + float(strategy["fixture_weight"]) * fixture_edge
        + float(strategy["form_weight"]) * player.form
        + float(strategy["ownership_weight"]) * player.selected_by_percent
        + float(strategy["secure_starter_weight"]) * secure_starter
        + float(strategy["defensive_contribution_weight"])
        * player.defensive_contribution_per_90
        * games
    )
    return score * availability(player) / 100


def _choose_transfer(
    owned: list[OwnedPlayer],
    candidates: list[Player],
    scores: dict[int, float],
    settings: SquadSettings,
    strategy: dict[str, Any],
) -> list[Transfer]:
    if int(strategy.get("max_recommended_transfers", 1)) < 1:
        return []
    if settings.free_transfers < 1 and int(strategy.get("max_points_hit", 0)) <= 0:
        return []

    current_ids = {item.player.id for item in owned}
    risky = [
        item
        for item in owned
        if availability(item.player) < 75
        or item.player.status in {"i", "s", "u"}
        or not item.player.can_select
    ]
    if not risky and bool(strategy.get("avoid_optional_transfers", True)):
        return []

    outgoing_pool = risky or sorted(owned, key=lambda item: scores[item.player.id])[:1]
    choices: list[tuple[float, Transfer]] = []
    for outgoing in outgoing_pool:
        sale = selling_price(outgoing.player.cost, outgoing.purchase_price)
        funds = sale + settings.bank
        for incoming in candidates:
            if incoming.id in current_ids or incoming.position != outgoing.player.position:
                continue
            if incoming.cost > funds or availability(incoming) < 90 or not incoming.can_select:
                continue
            transfer = Transfer(
                player_out=outgoing.player,
                player_in=incoming,
                selling_price=sale,
                buying_price=incoming.cost,
                points_hit=0,
            )
            _, _, errors = apply_and_validate_transfers(owned, [transfer], settings.bank)
            if errors:
                continue
            gain = scores[incoming.id] - scores[outgoing.player.id]
            choices.append((gain, transfer))

    if not choices:
        return []
    gain, best = max(choices, key=lambda item: item[0])
    threshold = float(strategy.get("min_transfer_gain", 2.5))
    if gain < threshold and availability(best.player_out) > 0:
        return []
    return [best]


def _choose_lineup(
    players: list[Player], scores: dict[int, float]
) -> tuple[list[Player], list[Player], Player]:
    by_position: dict[str, list[Player]] = defaultdict(list)
    for player in players:
        by_position[player.position].append(player)
    for group in by_position.values():
        group.sort(key=lambda player: scores[player.id], reverse=True)

    goalkeeper = by_position["GK"][0]
    reserve_goalkeeper = by_position["GK"][1]
    best_lineup: list[Player] | None = None
    best_score = float("-inf")
    for defenders in range(3, 6):
        for midfielders in range(2, 6):
            forwards = 10 - defenders - midfielders
            if not 1 <= forwards <= 3:
                continue
            selection = [
                goalkeeper,
                *by_position["DEF"][:defenders],
                *by_position["MID"][:midfielders],
                *by_position["FWD"][:forwards],
            ]
            total = sum(scores[player.id] for player in selection)
            if total > best_score:
                best_lineup = selection
                best_score = total
    if best_lineup is None:
        raise ValueError("Could not construct a legal starting XI")

    starting_ids = {player.id for player in best_lineup}
    bench = sorted(
        [
            player
            for player in players
            if player.id not in starting_ids and player.position != "GK"
        ],
        key=lambda player: scores[player.id],
        reverse=True,
    )
    return best_lineup, bench, reserve_goalkeeper


def _captains(
    lineup: list[Player],
    scores: dict[int, float],
    settings: SquadSettings,
    strategy: dict[str, Any],
) -> tuple[Player, Player]:
    min_availability = int(strategy.get("captain_min_availability", 90))
    eligible = [player for player in lineup if availability(player) >= min_availability]
    if len(eligible) < 2:
        eligible = sorted(lineup, key=availability, reverse=True)[: max(2, len(lineup))]

    current_captain = normalize_name(settings.captain)
    current_vice = normalize_name(settings.vice_captain)
    ownership_weight = float(strategy.get("captain_ownership_weight", 0.18))

    def captain_score(player: Player) -> float:
        one_week = max(player.expected_next, player.points_per_game, player.form, 2.0)
        premium = player.cost / 40
        continuity = 2.0 if normalize_name(player.name) == current_captain else 0.0
        if normalize_name(player.full_name) == current_captain:
            continuity = 2.0
        vice_continuity = 0.7 if normalize_name(player.full_name) == current_vice else 0.0
        return (
            one_week * availability(player) / 100
            + ownership_weight * player.selected_by_percent
            + premium
            + continuity
            + vice_continuity
            + 0.05 * scores[player.id]
        )

    ranked = sorted(eligible, key=captain_score, reverse=True)
    return ranked[0], ranked[1]


def recommend(
    event: Event,
    owned: list[OwnedPlayer],
    bootstrap: dict[str, Any],
    fixtures: list[dict[str, Any]],
    settings: SquadSettings,
    strategy: dict[str, Any],
) -> Recommendation:
    current_errors = validate_squad(item.player for item in owned)
    if current_errors:
        raise ValueError("Initial squad is illegal: " + "; ".join(current_errors))

    horizon = min(
        int(strategy.get("fixture_horizon", 5)),
        int(strategy.get("max_fixture_horizon", 6)),
    )
    difficulties = fixture_difficulties(fixtures, event.id, horizon)
    candidates = all_api_players(bootstrap["elements"], bootstrap["teams"])
    scores = {
        player.id: score_player(player, difficulties.get(player.team_id, []), strategy)
        for player in candidates
    }
    transfers = _choose_transfer(owned, candidates, scores, settings, strategy)
    proposed, remaining_bank, errors = apply_and_validate_transfers(
        owned, transfers, settings.bank
    )
    if errors:
        raise ValueError("Generated recommendation is illegal: " + "; ".join(errors))

    lineup, bench, reserve_goalkeeper = _choose_lineup(proposed, scores)
    captain, vice = _captains(lineup, scores, settings, strategy)
    questionable = [player for player in lineup if availability(player) < 90]
    confidence = "High" if not questionable and not transfers else "Medium"

    if transfers:
        transfer = transfers[0]
        transfer_text = (
            f"Use one free transfer: {transfer.player_out.name} to "
            f"{transfer.player_in.name}. The move remains within budget with "
            f"£{remaining_bank / 10:.1f}m left and passes all squad rules."
        )
    else:
        transfer_text = (
            "Roll the transfer. No urgent availability problem clears the configured "
            "multi-fixture gain threshold, so a points-free hold is preferred."
        )
    explanation = (
        f"{transfer_text} The XI balances official expected points, secure-start signals, "
        f"ownership, the next {horizon} Gameweeks, fixture difficulty and defensive "
        "contributions. Captaincy favors a reliable, highly owned premium."
    )

    return Recommendation(
        event=event,
        transfers=transfers,
        points_hit=sum(transfer.points_hit for transfer in transfers),
        captain=captain.name,
        vice_captain=vice.name,
        starting_xi=[player.name for player in lineup],
        bench=[player.name for player in bench],
        reserve_goalkeeper=reserve_goalkeeper.name,
        chip="None — save the chip",
        confidence=confidence,
        explanation=explanation,
        validation=[
            "15-player squad and position quotas valid",
            "Maximum three players per club valid",
            f"Transfer budget valid; projected bank £{remaining_bank / 10:.1f}m",
            f"Points hit {sum(transfer.points_hit for transfer in transfers)}",
        ],
    )


def fallback_recommendation(
    event: Event, settings: SquadSettings, reason: str
) -> Recommendation:
    by_position: dict[str, list[str]] = defaultdict(list)
    for entry in settings.entries:
        by_position[entry.position].append(entry.name)

    starting = [
        by_position["GK"][0],
        *by_position["DEF"][:4],
        *by_position["MID"][:4],
        *by_position["FWD"][:2],
    ]
    bench = [
        *by_position["MID"][4:],
        *by_position["DEF"][4:],
        *by_position["FWD"][2:],
    ]
    return Recommendation(
        event=event,
        transfers=[],
        points_hit=0,
        captain=settings.captain,
        vice_captain=settings.vice_captain,
        starting_xi=starting,
        bench=bench,
        reserve_goalkeeper=by_position["GK"][1],
        chip="None — save the chip",
        confidence="Low",
        explanation=(
            "Safe fallback: make no transfer and take no points hit because live inputs "
            f"could not be trusted ({reason}). Check late team news manually before the "
            "deadline; the configured captaincy and a legal 4-4-2 are retained."
        ),
        source="fallback",
        fallback=True,
        validation=["Fallback formation is 4-4-2", "No transfer or points hit proposed"],
    )
