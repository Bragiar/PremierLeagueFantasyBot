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
    Recommendation,
    SquadSettings,
    Transfer,
)
from fpl_bot.squad import (
    all_api_players,
    apply_and_validate_transfers,
    normalize_name,
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
    games = max(1, len(difficulties))
    sample_reliability = min(1.0, player.minutes / 450)
    performance_reliability = min(1.0, player.minutes / 90)
    official_prior = player.expected_next if player.expected_next > 0 else 2.0
    observed_rate = min(10.0, max(player.points_per_game, player.form, 2.0))
    expected = max(
        2.0,
        official_prior * (1 - sample_reliability)
        + observed_rate * sample_reliability,
    )
    base = expected * games
    fixture_edge = sum(3.2 - difficulty for difficulty in difficulties)

    if player.minutes > 0:
        secure_starter = min(1.0, player.starts * 75 / max(1, player.minutes))
    else:
        secure_starter = (
            0.25
            if bool(strategy.get("season_started", True))
            else min(1.0, 0.7 + player.selected_by_percent / 200)
        )

    score = (
        base
        + float(strategy["fixture_weight"]) * fixture_edge
        + float(strategy["form_weight"])
        * min(player.form, 10.0)
        * performance_reliability
        + float(strategy["ownership_weight"]) * player.selected_by_percent
        + float(strategy["secure_starter_weight"]) * secure_starter
        + float(strategy["defensive_contribution_weight"])
        * min(2.0, player.defensive_contribution_per_90 / 5.0)
        * performance_reliability
        * games
    )
    return score * availability(player) / 100


def score_player_for_gameweek(
    player: Player,
    difficulties: list[int],
    strategy: dict[str, Any],
) -> float:
    """Score a player only for the immediate Gameweek's free team decisions."""
    if not difficulties:
        return 0.0

    games = len(difficulties)
    sample_reliability = min(1.0, player.minutes / 450)
    performance_reliability = min(1.0, player.minutes / 90)
    official_prior = (
        player.expected_next if player.expected_next > 0 else 2.0 * games
    )
    observed_rate = min(10.0, max(player.points_per_game, player.form, 2.0))
    expected = (
        official_prior * (1 - sample_reliability)
        + observed_rate * games * sample_reliability
    )
    fixture_edge = sum(3.2 - difficulty for difficulty in difficulties)
    if player.minutes > 0:
        secure_starter = min(1.0, player.starts * 75 / max(1, player.minutes))
    else:
        secure_starter = (
            0.25
            if bool(strategy.get("season_started", True))
            else min(1.0, 0.7 + player.selected_by_percent / 200)
        )

    score = (
        expected
        + float(strategy.get("lineup_fixture_weight", 1.0)) * fixture_edge
        + float(strategy.get("lineup_form_weight", 0.25))
        * min(player.form, 10.0)
        * performance_reliability
        + float(strategy.get("lineup_ownership_weight", 0.02))
        * player.selected_by_percent
        + float(strategy.get("lineup_secure_starter_weight", 1.6))
        * secure_starter
        + float(strategy.get("lineup_defensive_contribution_weight", 0.2))
        * min(2.0, player.defensive_contribution_per_90 / 5.0)
        * performance_reliability
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
    limit = max(1, int(strategy.get("research_candidate_transfers", 3)))
    for gain, transfer in choices:
        option_id = f"transfer:{transfer.player_out.id}:{transfer.player_in.id}"
        is_engine_pick = bool(
            deterministic_transfers
            and transfer.player_out.id == deterministic_transfers[0].player_out.id
            and transfer.player_in.id == deterministic_transfers[0].player_in.id
        )
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


def _squad_objective(
    players: list[Player], scores: dict[int, float], bench_weight: float
) -> float:
    lineup, bench, reserve_goalkeeper = _choose_lineup(players, scores)
    captain_bonus = max(scores[player.id] for player in lineup)
    bench_score = sum(scores[player.id] for player in bench) + scores[reserve_goalkeeper.id]
    return sum(scores[player.id] for player in lineup) + captain_bonus + bench_weight * bench_score


def _optimizer_pool(
    candidates: list[Player], scores: dict[int, float]
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
) -> tuple[list[Player], float]:
    """Use a bounded multi-start local search for a legal 15-player squad."""
    pools = _optimizer_pool(candidates, scores)
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
            candidates, gameweek_scores, team_value, bench_weight=0.0
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
            candidates, horizon_scores, team_value, bench_weight=0.15
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
    scoring_strategy["season_started"] = event.id > 1
    transfer_scores = {
        player.id: score_player(
            player, difficulties.get(player.team_id, []), scoring_strategy
        )
        for player in candidates
    }
    deterministic_transfers = _choose_transfer(
        owned, candidates, transfer_scores, settings, strategy
    )
    engine_options = _engine_options(
        owned,
        candidates,
        transfer_scores,
        settings,
        strategy,
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
    captain, vice = _captains(lineup, gameweek_scores, settings, strategy)
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
        strategy,
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
        captain, vice = _captains(lineup, gameweek_scores, settings, strategy)

    questionable = [player for player in lineup if availability(player) < 90]
    confidence = (
        "High"
        if not questionable and not transfers and chosen_chip.id == "chip:none"
        else "Medium"
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
        f"estimated uplift {chosen_chip.projected_uplift:.1f}."
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
            strategy,
            transfers,
            chosen_chip.id,
            captain.name,
            chosen_chip.projected_uplift,
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
        validation=[
            "15-player squad and position quotas valid",
            "Maximum three players per club valid",
            f"Transfer budget valid; projected bank £{remaining_bank / 10:.1f}m",
            f"Points hit {sum(transfer.points_hit for transfer in transfers)}",
            f"Selected reviewed engine option {chosen_option.id}",
            f"Selected legal chip option {chosen_chip.id}",
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
