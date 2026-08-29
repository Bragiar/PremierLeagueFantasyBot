from __future__ import annotations

from collections import defaultdict
import re
from typing import Any, Iterable

from fpl_bot.models import (
    ChipOption,
    EngineOption,
    Event,
    OwnedPlayer,
    Player,
    PlayerProjection,
    Recommendation,
    SquadSettings,
    Transfer,
)
from fpl_bot.squad import (
    all_api_players,
    apply_and_validate_transfers,
    selling_price,
    validate_squad,
)


_NEWS_CHANCE_RE = re.compile(r"(?P<chance>\d{1,3})\s*%\s+chance\s+of\s+playing")
_NEWS_UNAVAILABLE_PHRASES = (
    "unknown return date",
    "not expected to play",
    "ruled out",
    "will miss",
    "out for",
    "unavailable",
    "suspended",
    "red card",
)
_NEWS_DOUBT_PHRASES = (
    "injury",
    "injured",
    "illness",
    "knock",
    "doubt",
    "fitness",
    "expected back",
    "international duty",
    "rested",
    "rotation",
)

_POSITION_BASELINE = {"GK": 2.2, "DEF": 2.4, "MID": 2.6, "FWD": 2.6}


def expected_minutes(player: Player, strategy: dict[str, Any]) -> float:
    """Estimate minutes without treating a green availability flag as a secure start."""
    available = availability(player)
    if available <= 0:
        return 0.0

    configured_completed = strategy.get("completed_gameweeks")
    completed = (
        max(player.starts, 1)
        if configured_completed is None
        else max(0, int(configured_completed))
    )
    price_floor = {"GK": 40, "DEF": 40, "MID": 45, "FWD": 45}[player.position]
    price_signal = min(22.0, max(0, player.cost - price_floor) * 0.45)
    ownership_signal = min(16.0, player.selected_by_percent * 0.2)
    prior = min(86.0, 46.0 + price_signal + ownership_signal)

    if completed <= 0:
        projected = prior
    else:
        observed_minutes = min(90.0, player.minutes / completed)
        start_share = min(1.0, player.starts / completed)
        observed_role = 0.65 * observed_minutes + 0.35 * 90.0 * start_share
        reliability = min(0.9, completed / 5)
        projected = prior * (1 - reliability) + observed_role * reliability
        if player.starts == 0:
            projected = min(projected, max(8.0, 20.0 - 3.0 * (completed - 1)))

    # Official expected points can rescue a new signing with little historical data,
    # but never turn a zero-minute squad player into a presumed starter by itself.
    if player.expected_next >= 4.0 and player.starts > 0:
        projected = max(projected, 65.0)
    elif player.expected_next >= 2.5 and player.starts > 0:
        projected = max(projected, 50.0)
    return max(0.0, min(90.0, projected * available / 100))


def _underlying_attack_signal(player: Player) -> float:
    if player.minutes <= 0:
        return 0.0
    per_90 = player.expected_goal_involvements * 90 / player.minutes
    return min(1.25, max(0.0, per_90))


def _projection_reliability(player: Player) -> float:
    return min(0.35, player.minutes / 900)


def _low_minutes_multiplier(minutes: float) -> float:
    """Discount cameo roles while leaving plausible starters untouched."""
    return min(1.0, max(0.0, minutes) / 45.0)


def _risk_mode(strategy: dict[str, Any]) -> str:
    mode = str(strategy.get("mini_league_mode", "balanced")).strip().lower()
    return mode if mode in {"balanced", "protect", "chase"} else "balanced"


def news_availability(player: Player) -> int | None:
    """Translate official FPL news into a conservative availability signal."""
    news = " ".join(player.news.lower().split())
    if not news:
        return None

    chance_match = _NEWS_CHANCE_RE.search(news)
    if chance_match:
        return max(0, min(100, int(chance_match.group("chance"))))
    if any(phrase in news for phrase in _NEWS_UNAVAILABLE_PHRASES):
        return 0
    if any(phrase in news for phrase in _NEWS_DOUBT_PHRASES):
        return 50
    return None


def availability(player: Player) -> int:
    if not player.can_select or player.status in {"i", "s", "u"}:
        return 0
    base_availability: int
    if player.chance_next is not None:
        base_availability = max(0, min(100, player.chance_next))
    else:
        base_availability = 100 if player.status == "a" else 75
    news_signal = news_availability(player)
    return (
        base_availability
        if news_signal is None
        else min(base_availability, news_signal)
    )


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
    """Score a player across the planning horizon for transfer decisions."""
    if not difficulties:
        return 0.0
    games = len(difficulties)
    reliability = _projection_reliability(player)
    official_prior = (
        player.expected_next
        if player.expected_next > 0
        else _POSITION_BASELINE[player.position]
    )
    observed_rate = min(9.0, max(player.points_per_game, player.form, 0.0))
    expected_rate = official_prior * (1 - reliability) + observed_rate * reliability
    base = expected_rate * games
    fixture_edge = sum(3.2 - difficulty for difficulty in difficulties)
    minutes_share = expected_minutes(player, strategy) / 90
    form_delta = min(3.0, max(-3.0, player.form - official_prior))
    attack_signal = _underlying_attack_signal(player)
    score = (
        base
        + float(strategy["fixture_weight"]) * fixture_edge
        + float(strategy["form_weight"]) * form_delta * reliability * games
        + float(strategy.get("underlying_stats_weight", 0.7))
        * attack_signal
        * reliability
        * games
        + float(strategy.get("secure_starter_weight", 1.6))
        * (minutes_share - 0.65)
        * games
        + float(strategy["defensive_contribution_weight"])
        * min(2.0, player.defensive_contribution_per_90 / 5.0)
        * reliability
        * games
    )
    maximum = float(strategy.get("max_player_gameweek_projection", 15.0)) * games
    adjusted = (
        score
        * _low_minutes_multiplier(expected_minutes(player, strategy))
        * availability(player)
        / 100
    )
    return max(0.0, min(maximum, adjusted))


def score_player_for_gameweek(
    player: Player,
    difficulties: list[int],
    strategy: dict[str, Any],
) -> float:
    """Score a player only for the immediate Gameweek's free team decisions."""
    if not difficulties:
        return 0.0

    games = len(difficulties)
    reliability = _projection_reliability(player)
    official_prior = (
        player.expected_next
        if player.expected_next > 0
        else _POSITION_BASELINE[player.position] * games
    )
    observed_rate = min(9.0, max(player.points_per_game, player.form, 0.0))
    expected = (
        official_prior * (1 - reliability)
        + observed_rate * games * reliability
    )
    fixture_edge = sum(3.2 - difficulty for difficulty in difficulties)
    minutes_share = expected_minutes(player, strategy) / 90
    official_rate = official_prior / games
    form_delta = min(3.0, max(-3.0, player.form - official_rate))
    attack_signal = _underlying_attack_signal(player)
    score = (
        expected
        + float(strategy.get("lineup_fixture_weight", 1.0)) * fixture_edge
        + float(strategy.get("lineup_form_weight", 0.25))
        * form_delta
        * reliability
        * games
        + float(strategy.get("lineup_underlying_stats_weight", 0.8))
        * attack_signal
        * reliability
        * games
        + float(strategy.get("lineup_secure_starter_weight", 1.6))
        * (minutes_share - 0.65)
        * games
        + float(strategy.get("lineup_defensive_contribution_weight", 0.2))
        * min(2.0, player.defensive_contribution_per_90 / 5.0)
        * reliability
        * games
    )
    maximum = float(strategy.get("max_player_gameweek_projection", 15.0)) * games
    adjusted = (
        score
        * _low_minutes_multiplier(expected_minutes(player, strategy))
        * availability(player)
        / 100
    )
    return max(0.0, min(maximum, adjusted))


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
    if not risky and bool(strategy.get("avoid_optional_transfers", True)):
        completed = int(strategy.get("completed_gameweeks", 0))
        minimum_sample = int(
            strategy.get("optional_transfer_min_completed_gameweeks", 2)
        )
        exception_gain = float(
            strategy.get("optional_transfer_exception_gain", threshold + 4.0)
        )
        if completed < minimum_sample or gain < exception_gain:
            return []
    if gain < threshold and availability(best.player_out) > 0:
        return []
    return [best]


def _engine_options(
    owned: list[OwnedPlayer],
    candidates: list[Player],
    scores: dict[int, float],
    settings: SquadSettings,
    strategy: dict[str, Any],
    deterministic_transfers: list[Transfer],
) -> list[EngineOption]:
    """Expose hold plus the strongest legal one-transfer alternatives for review."""
    options = [
        EngineOption(
            id="hold",
            action="Roll the free transfer",
            projected_gain=0.0,
            rationale="Preserves flexibility and avoids acting on a marginal projection.",
        )
    ]
    if settings.free_transfers < 1 or int(strategy.get("max_recommended_transfers", 1)) < 1:
        return options

    current_ids = {item.player.id for item in owned}
    choices: list[tuple[float, Transfer]] = []
    for outgoing in owned:
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
            choices.append((scores[incoming.id] - scores[outgoing.player.id], transfer))

    choices.sort(key=lambda item: item[0], reverse=True)
    minimum_gain = float(strategy.get("min_transfer_gain", 2.5))
    horizon = max(1, int(strategy.get("fixture_horizon", 5)))
    maximum_gain = float(
        strategy.get("max_transfer_gain_per_gameweek", 4.0)
    ) * horizon
    limit = max(1, int(strategy.get("research_candidate_transfers", 3)))
    for gain, transfer in choices:
        option_id = f"transfer:{transfer.player_out.id}:{transfer.player_in.id}"
        is_engine_pick = bool(
            deterministic_transfers
            and transfer.player_out.id == deterministic_transfers[0].player_out.id
            and transfer.player_in.id == deterministic_transfers[0].player_in.id
        )
        if gain > maximum_gain:
            continue
        if gain < minimum_gain and not is_engine_pick:
            continue
        options.append(
            EngineOption(
                id=option_id,
                action=f"{transfer.player_out.name} → {transfer.player_in.name}",
                projected_gain=gain,
                rationale=(
                    f"Engine scores {transfer.player_in.name} {gain:.1f} points above "
                    f"{transfer.player_out.name} over the configured horizon; "
                    f"incoming availability is {availability(transfer.player_in)}%."
                ),
                transfer=transfer,
            )
        )
        if len(options) - 1 >= limit:
            break
    if deterministic_transfers:
        transfer = deterministic_transfers[0]
        option_id = f"transfer:{transfer.player_out.id}:{transfer.player_in.id}"
        if not any(option.id == option_id for option in options):
            gain = scores[transfer.player_in.id] - scores[transfer.player_out.id]
            options.append(
                EngineOption(
                    id=option_id,
                    action=f"{transfer.player_out.name} → {transfer.player_in.name}",
                    projected_gain=gain,
                    rationale=(
                        "The deterministic safety policy selected this legal move for an "
                        f"availability risk; projected gain is {gain:.1f}."
                    ),
                    transfer=transfer,
                )
            )
    return options


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
    strategy: dict[str, Any],
) -> tuple[Player, Player]:
    min_availability = int(strategy.get("captain_min_availability", 90))
    minimum_minutes = float(strategy.get("captain_min_expected_minutes", 60))
    eligible = [
        player
        for player in lineup
        if availability(player) >= min_availability
        and expected_minutes(player, strategy) >= minimum_minutes
    ]
    if len(eligible) < 2:
        eligible = sorted(
            lineup,
            key=lambda player: (expected_minutes(player, strategy), availability(player)),
            reverse=True,
        )[: max(2, len(lineup))]

    ranked = sorted(
        eligible,
        key=lambda player: _captain_score(player, scores, strategy),
        reverse=True,
    )
    return ranked[0], ranked[1]


def _captain_score(
    player: Player, scores: dict[int, float], strategy: dict[str, Any]
) -> float:
    mode = _risk_mode(strategy)
    ownership_tiebreak = {
        "balanced": 0.0,
        "protect": float(strategy.get("protect_captain_ownership_weight", 0.012)),
        "chase": -float(strategy.get("chase_captain_ownership_weight", 0.004)),
    }[mode]
    ceiling = _underlying_attack_signal(player) * float(
        strategy.get("captain_ceiling_weight", 0.35)
    )
    minutes_factor = expected_minutes(player, strategy) / 90
    return (
        scores[player.id] * (0.75 + 0.25 * minutes_factor)
        + ceiling
        + ownership_tiebreak * player.selected_by_percent
    )


def _captain_margin(
    lineup: list[Player], scores: dict[int, float], strategy: dict[str, Any]
) -> float:
    ranked = sorted(
        (_captain_score(player, scores, strategy) for player in lineup), reverse=True
    )
    return ranked[0] - ranked[1] if len(ranked) >= 2 else 0.0


def _squad_objective(
    players: list[Player], scores: dict[int, float], bench_weight: float
) -> float:
    lineup, bench, reserve_goalkeeper = _choose_lineup(players, scores)
    captain_bonus = max(scores[player.id] for player in lineup)
    bench_score = sum(scores[player.id] for player in bench) + scores[reserve_goalkeeper.id]
    return sum(scores[player.id] for player in lineup) + captain_bonus + bench_weight * bench_score


def _optimizer_pool(
    candidates: list[Player], scores: dict[int, float], strategy: dict[str, Any]
) -> dict[str, list[Player]]:
    pools: dict[str, list[Player]] = {}
    for position in ("GK", "DEF", "MID", "FWD"):
        eligible = [
            player
            for player in candidates
            if player.position == position
            and player.can_select
            and availability(player) >= 90
            and player.cost > 0
            and expected_minutes(player, strategy)
            >= float(strategy.get("optimizer_min_expected_minutes", 25))
        ]
        strongest = sorted(eligible, key=lambda player: scores[player.id], reverse=True)[:45]
        cheapest = sorted(eligible, key=lambda player: (player.cost, -scores[player.id]))[:20]
        unique = {player.id: player for player in [*strongest, *cheapest]}
        pools[position] = list(unique.values())
    return pools


def _cheapest_legal_squad(
    pools: dict[str, list[Player]], scores: dict[int, float]
) -> list[Player]:
    quotas = {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}
    selected: list[Player] = []
    club_counts: dict[int, int] = defaultdict(int)
    for position, quota in quotas.items():
        ranked = sorted(
            pools[position], key=lambda player: (player.cost, -scores[player.id])
        )
        for player in ranked:
            if club_counts[player.team_id] >= 3:
                continue
            selected.append(player)
            club_counts[player.team_id] += 1
            if sum(item.position == position for item in selected) == quota:
                break
        if sum(item.position == position for item in selected) != quota:
            raise ValueError(f"Could not construct an optimizer squad at {position}")
    errors = validate_squad(selected)
    if errors:
        raise ValueError("Optimizer starting squad is illegal: " + "; ".join(errors))
    return selected


def _optimize_squad(
    candidates: list[Player],
    scores: dict[int, float],
    budget: int,
    *,
    bench_weight: float,
    strategy: dict[str, Any] | None = None,
) -> tuple[list[Player], float]:
    """Use a bounded multi-start local search for a legal 15-player squad."""
    strategy = strategy or {}
    pools = _optimizer_pool(candidates, scores, strategy)
    starting = _cheapest_legal_squad(pools, scores)
    if sum(player.cost for player in starting) > budget:
        raise ValueError("No legal optimizer squad fits the available team value")

    def improve(mode: str) -> tuple[list[Player], float]:
        squad = list(starting)
        objective = _squad_objective(squad, scores, bench_weight)
        for _ in range(35):
            current_ids = {player.id for player in squad}
            current_cost = sum(player.cost for player in squad)
            club_counts: dict[int, int] = defaultdict(int)
            for player in squad:
                club_counts[player.team_id] += 1
            best: tuple[float, float, int, Player] | None = None
            for index, outgoing in enumerate(squad):
                for incoming in pools[outgoing.position]:
                    if incoming.id in current_ids:
                        continue
                    new_cost = current_cost - outgoing.cost + incoming.cost
                    if new_cost > budget:
                        continue
                    incoming_club_count = club_counts[incoming.team_id]
                    if incoming.team_id == outgoing.team_id:
                        incoming_club_count -= 1
                    if incoming_club_count >= 3:
                        continue
                    proposed = list(squad)
                    proposed[index] = incoming
                    new_objective = _squad_objective(proposed, scores, bench_weight)
                    gain = new_objective - objective
                    if gain <= 0.001:
                        continue
                    extra_cost = max(1, incoming.cost - outgoing.cost)
                    priority = gain if mode == "absolute" else gain / extra_cost
                    candidate = (priority, new_objective, index, incoming)
                    if best is None or candidate[:2] > best[:2]:
                        best = candidate
            if best is None:
                break
            _, objective, index, incoming = best
            squad[index] = incoming
        return squad, objective

    attempts = [improve("absolute"), improve("value")]
    best_squad, best_objective = max(attempts, key=lambda item: item[1])
    errors = validate_squad(best_squad)
    if errors or sum(player.cost for player in best_squad) > budget:
        raise ValueError("Optimizer produced an illegal squad")
    return best_squad, best_objective


def _chip_is_available(settings: SquadSettings, event_id: int, chip: str) -> bool:
    half = "first_half" if event_id <= 19 else "second_half"
    return settings.chips.get(half, {}).get(chip) == "available"


def _chip_options(
    event: Event,
    owned: list[OwnedPlayer],
    current_squad: list[Player],
    candidates: list[Player],
    gameweek_scores: dict[int, float],
    horizon_scores: dict[int, float],
    captain: Player,
    bench: list[Player],
    reserve_goalkeeper: Player,
    settings: SquadSettings,
    strategy: dict[str, Any],
) -> list[ChipOption]:
    half = "first" if event.id <= 19 else "second"
    expiry = 19 if event.id <= 19 else 38
    options = [
        ChipOption(
            id="chip:none",
            chip="None",
            projected_uplift=0.0,
            rationale=f"Preserve the {half}-half chips for a stronger opportunity before GW{expiry}.",
        )
    ]
    if _chip_is_available(settings, event.id, "triple_captain"):
        uplift = gameweek_scores[captain.id]
        options.append(
            ChipOption(
                id="chip:triple_captain",
                chip="Triple Captain",
                projected_uplift=uplift,
                rationale=(
                    f"Adds one extra copy of {captain.name}'s projected {uplift:.1f} points."
                ),
            )
        )
    if _chip_is_available(settings, event.id, "bench_boost"):
        uplift = sum(gameweek_scores[player.id] for player in bench)
        uplift += gameweek_scores[reserve_goalkeeper.id]
        options.append(
            ChipOption(
                id="chip:bench_boost",
                chip="Bench Boost",
                projected_uplift=uplift,
                rationale=f"The four substitutes project for {uplift:.1f} points in total.",
            )
        )

    team_value = settings.bank + sum(
        selling_price(item.player.cost, item.purchase_price) for item in owned
    )
    if event.id != 1 and _chip_is_available(settings, event.id, "free_hit"):
        free_hit_squad, optimized = _optimize_squad(
            candidates,
            gameweek_scores,
            team_value,
            bench_weight=0.0,
            strategy=strategy,
        )
        baseline = _squad_objective(current_squad, gameweek_scores, 0.0)
        options.append(
            ChipOption(
                id="chip:free_hit",
                chip="Free Hit",
                projected_uplift=max(0.0, optimized - baseline),
                rationale=(
                    "Bounded one-Gameweek legal squad search compared with the current best XI."
                ),
                squad=tuple(free_hit_squad),
            )
        )
    if _chip_is_available(settings, event.id, "wildcard"):
        wildcard_squad, optimized = _optimize_squad(
            candidates,
            horizon_scores,
            team_value,
            bench_weight=0.15,
            strategy=strategy,
        )
        baseline = _squad_objective(current_squad, horizon_scores, 0.15)
        options.append(
            ChipOption(
                id="chip:wildcard",
                chip="Wildcard",
                projected_uplift=max(0.0, optimized - baseline),
                rationale=(
                    "Bounded permanent-squad search across the configured planning horizon."
                ),
                squad=tuple(wildcard_squad),
            )
        )
    return options


def _default_chip_id(
    event: Event, options: list[ChipOption], strategy: dict[str, Any]
) -> str:
    expiry_pressure = event.id >= (16 if event.id <= 19 else 35)
    if (
        bool(strategy.get("save_chips_by_default", True))
        and not expiry_pressure
        and not bool(strategy.get("allow_exceptional_early_chip", False))
    ):
        return "chip:none"
    exceptional = {
        "chip:triple_captain": float(strategy.get("triple_captain_exceptional_uplift", 12)),
        "chip:bench_boost": float(strategy.get("bench_boost_exceptional_uplift", 20)),
        "chip:free_hit": float(strategy.get("free_hit_exceptional_uplift", 25)),
        "chip:wildcard": float(strategy.get("wildcard_exceptional_uplift", 35)),
    }
    eligible = [
        option
        for option in options
        if option.id != "chip:none"
        and option.projected_uplift >= exceptional.get(option.id, float("inf"))
    ]
    if bool(strategy.get("save_chips_by_default", True)) and not expiry_pressure:
        return max(eligible, key=lambda option: option.projected_uplift).id if eligible else "chip:none"
    non_none = [option for option in options if option.id != "chip:none"]
    return max(non_none, key=lambda option: option.projected_uplift).id if non_none else "chip:none"


def _confidence_assessment(
    event: Event,
    lineup: list[Player],
    captain: Player,
    gameweek_scores: dict[int, float],
    engine_options: list[EngineOption],
    selected_option_id: str,
    strategy: dict[str, Any],
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    completed = max(0, event.id - 1)
    if completed < int(strategy.get("high_confidence_min_completed_gameweeks", 3)):
        reasons.append(
            f"Only {completed} completed Gameweek{'s' if completed != 1 else ''} of current-season evidence."
        )

    low_minutes = [
        player
        for player in lineup
        if expected_minutes(player, strategy)
        < float(strategy.get("lineup_low_minutes_threshold", 55))
    ]
    if low_minutes:
        reasons.append(
            "Expected-minutes uncertainty: "
            + ", ".join(player.name for player in low_minutes[:3])
            + "."
        )

    captain_minutes = expected_minutes(captain, strategy)
    margin = _captain_margin(lineup, gameweek_scores, strategy)
    if captain_minutes < float(strategy.get("captain_min_expected_minutes", 60)):
        reasons.append(f"{captain.name} projects below 60 minutes.")
    if margin < float(strategy.get("captain_high_confidence_margin", 0.75)):
        reasons.append(
            f"Captaincy is close: the top-two model margin is only {margin:.2f} points."
        )

    best_transfer_gain = max(
        (
            option.projected_gain
            for option in engine_options
            if option.id != "hold"
        ),
        default=0.0,
    )
    if (
        selected_option_id == "hold"
        and best_transfer_gain
        >= float(strategy.get("confidence_transfer_conflict_gain", 6.0))
    ):
        reasons.append(
            f"The hold policy conflicts with a shortlisted model gain of {best_transfer_gain:.1f}."
        )

    severe = captain_minutes < 45 or any(
        expected_minutes(player, strategy) < 25 for player in lineup
    )
    if severe:
        return "Low", reasons
    if reasons:
        return "Medium", reasons
    return "High", ["Stable expected minutes and clear model margins."]


def _build_player_projections(
    proposed: list[Player],
    lineup: list[Player],
    bench: list[Player],
    reserve_goalkeeper: Player,
    captain: Player,
    vice: Player,
    engine_options: list[EngineOption],
    scores: dict[int, float],
    strategy: dict[str, Any],
) -> tuple[PlayerProjection, ...]:
    roles: dict[int, str] = {player.id: "squad" for player in proposed}
    roles.update({player.id: "starter" for player in lineup})
    roles.update({player.id: "bench" for player in bench})
    roles[reserve_goalkeeper.id] = "reserve goalkeeper"
    roles[vice.id] = "vice-captain"
    roles[captain.id] = "captain"
    tracked = {player.id: player for player in proposed}
    for option in engine_options:
        if option.transfer is None:
            continue
        tracked[option.transfer.player_in.id] = option.transfer.player_in
        tracked[option.transfer.player_out.id] = option.transfer.player_out
        roles.setdefault(option.transfer.player_in.id, "transfer candidate")
        roles.setdefault(option.transfer.player_out.id, "transfer candidate")
    return tuple(
        PlayerProjection(
            player_id=player.id,
            player=player.name,
            expected_points=scores.get(player.id, 0.0),
            expected_minutes=expected_minutes(player, strategy),
            role=roles.get(player.id, "tracked"),
        )
        for player in sorted(tracked.values(), key=lambda item: item.id)
    )


def recommend(
    event: Event,
    owned: list[OwnedPlayer],
    bootstrap: dict[str, Any],
    fixtures: list[dict[str, Any]],
    settings: SquadSettings,
    strategy: dict[str, Any],
    selected_option_id: str | None = None,
    selected_chip_id: str | None = None,
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
    scoring_strategy = dict(strategy)
    scoring_strategy["completed_gameweeks"] = max(0, event.id - 1)
    transfer_scores = {
        player.id: score_player(
            player, difficulties.get(player.team_id, []), scoring_strategy
        )
        for player in candidates
    }
    deterministic_transfers = _choose_transfer(
        owned, candidates, transfer_scores, settings, scoring_strategy
    )
    engine_options = _engine_options(
        owned,
        candidates,
        transfer_scores,
        settings,
        scoring_strategy,
        deterministic_transfers,
    )
    default_option_id = (
        "hold"
        if not deterministic_transfers
        else (
            f"transfer:{deterministic_transfers[0].player_out.id}:"
            f"{deterministic_transfers[0].player_in.id}"
        )
    )
    chosen_option_id = selected_option_id or default_option_id
    chosen_option = next(
        (option for option in engine_options if option.id == chosen_option_id), None
    )
    if chosen_option is None:
        raise ValueError(f"Unknown or non-shortlisted engine option {chosen_option_id!r}")
    transfers = [] if chosen_option.transfer is None else [chosen_option.transfer]
    proposed, remaining_bank, errors = apply_and_validate_transfers(
        owned, transfers, settings.bank
    )
    if errors:
        raise ValueError("Generated recommendation is illegal: " + "; ".join(errors))

    gameweek_difficulties = fixture_difficulties(fixtures, event.id, 1)
    gameweek_scores = {
        player.id: score_player_for_gameweek(
            player, gameweek_difficulties.get(player.team_id, []), scoring_strategy
        )
        for player in candidates
    }
    lineup, bench, reserve_goalkeeper = _choose_lineup(proposed, gameweek_scores)
    captain, vice = _captains(lineup, gameweek_scores, scoring_strategy)
    chip_options = _chip_options(
        event,
        owned,
        proposed,
        candidates,
        gameweek_scores,
        transfer_scores,
        captain,
        bench,
        reserve_goalkeeper,
        settings,
        scoring_strategy,
    )
    chosen_chip_id = selected_chip_id or _default_chip_id(event, chip_options, strategy)
    chosen_chip = next(
        (option for option in chip_options if option.id == chosen_chip_id), None
    )
    if chosen_chip is None:
        raise ValueError(f"Unknown or unavailable chip option {chosen_chip_id!r}")

    if chosen_chip.id in {"chip:free_hit", "chip:wildcard"}:
        proposed = list(chosen_chip.squad)
        transfers = []
        chosen_option = next(option for option in engine_options if option.id == "hold")
        team_value = settings.bank + sum(
            selling_price(item.player.cost, item.purchase_price) for item in owned
        )
        remaining_bank = team_value - sum(player.cost for player in proposed)
        errors = validate_squad(proposed)
        if errors or remaining_bank < 0:
            raise ValueError("Selected chip squad failed final legality validation")
        lineup, bench, reserve_goalkeeper = _choose_lineup(proposed, gameweek_scores)
        captain, vice = _captains(lineup, gameweek_scores, scoring_strategy)

    confidence, confidence_reasons = _confidence_assessment(
        event,
        lineup,
        captain,
        gameweek_scores,
        engine_options,
        chosen_option.id,
        scoring_strategy,
    )

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
        f"{transfer_text} Transfers are assessed across the next {horizon} Gameweeks. "
        "The starting XI, bench order and captaincy are assessed separately for this "
        f"Gameweek because those changes are free. Chip choice: {chosen_chip.chip}; "
        f"estimated uplift {chosen_chip.projected_uplift:.1f}. Risk mode: "
        f"{_risk_mode(scoring_strategy)}."
    )

    chip_text = {
        "chip:none": "None — save the chip",
        "chip:triple_captain": f"Triple Captain — {captain.name}",
        "chip:bench_boost": "Bench Boost",
        "chip:free_hit": "Free Hit",
        "chip:wildcard": "Wildcard",
    }[chosen_chip.id]

    rolling_plan = None
    plan_validation = "Rolling plan unavailable"
    try:
        # Imported here so the planner can reuse the engine's validated scoring helpers
        # without creating an import cycle during module initialization.
        from fpl_bot.planner import build_rolling_plan

        rolling_plan = build_rolling_plan(
            event,
            list(bootstrap.get("events", [])),
            owned,
            proposed,
            candidates,
            fixtures,
            settings,
            scoring_strategy,
            transfers,
            chosen_chip.id,
            captain.name,
            chosen_chip.projected_uplift,
            confidence,
        )
        plan_validation = (
            f"Reachable {rolling_plan.horizon}-Gameweek rolling route validated"
        )
    except (KeyError, TypeError, ValueError) as exc:
        plan_validation = f"Rolling plan unavailable: {type(exc).__name__}"

    return Recommendation(
        event=event,
        transfers=transfers,
        points_hit=sum(transfer.points_hit for transfer in transfers),
        captain=captain.name,
        vice_captain=vice.name,
        starting_xi=[player.name for player in lineup],
        bench=[player.name for player in bench],
        reserve_goalkeeper=reserve_goalkeeper.name,
        chip=chip_text,
        confidence=confidence,
        explanation=explanation,
        selected_option_id=chosen_option.id,
        engine_options=engine_options,
        selected_chip_id=chosen_chip.id,
        chip_options=chip_options,
        rolling_plan=rolling_plan,
        player_projections=_build_player_projections(
            proposed,
            lineup,
            bench,
            reserve_goalkeeper,
            captain,
            vice,
            engine_options,
            gameweek_scores,
            scoring_strategy,
        ),
        confidence_reasons=confidence_reasons,
        risk_mode=_risk_mode(scoring_strategy),
        validation=[
            "15-player squad and position quotas valid",
            "Maximum three players per club valid",
            f"Transfer budget valid; projected bank £{remaining_bank / 10:.1f}m",
            f"Points hit {sum(transfer.points_hit for transfer in transfers)}",
            f"Selected reviewed engine option {chosen_option.id}",
            f"Selected legal chip option {chosen_chip.id}",
            "Projection sanity bounds passed",
            f"Mini-league risk mode {_risk_mode(scoring_strategy)}",
            plan_validation,
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
