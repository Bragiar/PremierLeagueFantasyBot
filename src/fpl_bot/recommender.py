from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
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


@dataclass(frozen=True)
class _TransferChoice:
    gain: float
    price_priority: float
    transfer: Transfer
    timing_notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class _TransferBundleChoice:
    gain: float
    price_priority: float
    transfers: tuple[Transfer, ...]
    timing_notes: tuple[str, ...] = ()


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


def _price_prior_rate(player: Player) -> float:
    """Estimate a sustainable points rate without repeating short-term form forever."""
    price_floor = {"GK": 40, "DEF": 40, "MID": 45, "FWD": 45}[player.position]
    price_weight = {"GK": 0.08, "DEF": 0.10, "MID": 0.07, "FWD": 0.06}[
        player.position
    ]
    ceiling = {"GK": 5.0, "DEF": 5.5, "MID": 7.0, "FWD": 8.0}[player.position]
    return min(ceiling, 2.3 + max(0, player.cost - price_floor) * price_weight)


def _observed_points_rate(player: Player) -> float:
    """Smooth a short hot or cold streak against the season points rate."""
    season = max(0.0, player.points_per_game)
    recent = max(0.0, player.form)
    if season == 0:
        return min(9.0, recent)
    if recent == 0:
        return min(9.0, season)
    return min(9.0, 0.7 * season + 0.3 * recent)


def _blended_points_rate(player: Player, official_rate: float) -> float:
    """Blend FPL's short-term estimate and observed returns with a stable prior."""
    observed_rate = _observed_points_rate(player)
    observed_weight = min(0.45, player.minutes / 1800)
    official_weight = 0.25
    stable_weight = max(0.0, 1 - observed_weight - official_weight)
    return (
        _price_prior_rate(player) * stable_weight
        + official_rate * official_weight
        + observed_rate * observed_weight
    )


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
    immediate_prior = (
        player.expected_next
        if player.expected_next > 0
        else _POSITION_BASELINE[player.position]
    )
    observed_rate = _observed_points_rate(player)
    immediate_rate = _blended_points_rate(player, immediate_prior)
    sustainable_reliability = min(0.45, player.minutes / 1800)
    sustainable_rate = (
        _price_prior_rate(player) * (1 - sustainable_reliability)
        + observed_rate * sustainable_reliability
    )
    # FPL's ep_next is an immediate-Gameweek estimate. Repeating it across the whole
    # planning horizon badly overstates a recent hot streak, so later matches regress
    # toward a price-informed prior as the evidence horizon expands.
    base = immediate_rate + sustainable_rate * max(0, games - 1)
    fixture_edge = sum(3.2 - difficulty for difficulty in difficulties)
    minutes_share = expected_minutes(player, strategy) / 90
    form_delta = min(3.0, max(-3.0, player.form - immediate_prior))
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
    official_rate = official_prior / games
    expected = _blended_points_rate(player, official_rate) * games
    fixture_edge = sum(3.2 - difficulty for difficulty in difficulties)
    minutes_share = expected_minutes(player, strategy) / 90
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


def _price_projection(player: Player, offset: int = 0) -> tuple[float | None, int]:
    if bool(player.raw.get("price_change_calibrating")):
        return None, 0
    projections = player.raw.get("price_change_projections", [])
    if not isinstance(projections, list):
        return None, 0
    for raw in projections:
        if not isinstance(raw, dict):
            continue
        try:
            projection_offset = int(raw.get("offset", -1))
        except (TypeError, ValueError):
            continue
        if projection_offset != offset:
            continue
        try:
            return float(raw.get("projected_percent")), int(raw.get("likelihood", 0))
        except (TypeError, ValueError):
            return None, 0
    return None, 0


def _price_timing(
    outgoing: OwnedPlayer,
    incoming: Player,
    strategy: dict[str, Any],
) -> tuple[float, tuple[str, ...]]:
    """Describe imminent affordability changes without converting cash into points."""
    warning = float(strategy.get("price_change_warning_threshold", 90.0))
    priority = 0.0
    notes: list[str] = []
    out_projection, out_likelihood = _price_projection(outgoing.player)
    current_sale = selling_price(outgoing.player.cost, outgoing.purchase_price)
    after_drop = selling_price(
        max(0, outgoing.player.cost - 1), outgoing.purchase_price
    )
    if (
        out_projection is not None
        and out_projection <= -warning
        and out_likelihood < 0
        and after_drop < current_sale
    ):
        priority += current_sale - after_drop
        notes.append(
            f"{outgoing.player.name} projects {out_projection:.0f}% toward a fall; "
            f"that fall would cut the selling price by £{(current_sale - after_drop) / 10:.1f}m."
        )

    in_projection, in_likelihood = _price_projection(incoming)
    if (
        in_projection is not None
        and in_projection >= warning
        and in_likelihood > 0
    ):
        priority += 1.0
        notes.append(
            f"{incoming.name} projects {in_projection:.0f}% toward a rise, so waiting "
            "could add £0.1m to the buying price."
        )
    return priority, tuple(notes)


def _transfer_squad_objective(
    players: list[Player], scores: dict[int, float], bench_weight: float
) -> float:
    """Value the best XI and cover without inventing a five-week captaincy bonus."""
    lineup, bench, reserve_goalkeeper = _choose_lineup(players, scores)
    bench_score = sum(scores[player.id] for player in bench) + scores[reserve_goalkeeper.id]
    return sum(scores[player.id] for player in lineup) + bench_weight * bench_score


def _transfer_choices(
    owned: list[OwnedPlayer],
    candidates: list[Player],
    scores: dict[int, float],
    settings: SquadSettings,
    strategy: dict[str, Any],
) -> list[_TransferChoice]:
    current_ids = {item.player.id for item in owned}
    bench_weight = float(
        strategy.get(
            "transfer_bench_weight", strategy.get("planner_bench_weight", 0.08)
        )
    )
    baseline = _transfer_squad_objective(
        [item.player for item in owned], scores, bench_weight
    )
    choices: list[_TransferChoice] = []
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
            proposed, _, errors = apply_and_validate_transfers(
                owned, [transfer], settings.bank
            )
            if errors:
                continue
            gain = _transfer_squad_objective(proposed, scores, bench_weight) - baseline
            price_priority, timing_notes = _price_timing(
                outgoing, incoming, strategy
            )
            choices.append(
                _TransferChoice(gain, price_priority, transfer, timing_notes)
            )
    return choices


def _owned_after_players(
    players: list[Player], previous: list[OwnedPlayer]
) -> list[OwnedPlayer]:
    purchase_prices = {item.player.id: item.purchase_price for item in previous}
    return [
        OwnedPlayer(player, purchase_prices.get(player.id, player.cost))
        for player in players
    ]


def _pair_transfer_choices(
    owned: list[OwnedPlayer],
    candidates: list[Player],
    scores: dict[int, float],
    settings: SquadSettings,
    strategy: dict[str, Any],
    singles: list[_TransferChoice],
) -> list[_TransferBundleChoice]:
    if settings.free_transfers < 2 or int(strategy.get("max_recommended_transfers", 1)) < 2:
        return []

    bench_weight = float(
        strategy.get(
            "transfer_bench_weight", strategy.get("planner_bench_weight", 0.08)
        )
    )
    baseline = _transfer_squad_objective(
        [item.player for item in owned], scores, bench_weight
    )
    seed_limit = max(4, int(strategy.get("immediate_pair_first_seeds", 12)))
    second_limit = max(3, int(strategy.get("immediate_pair_second_seeds", 8)))
    ranked_singles = sorted(
        singles, key=lambda choice: (choice.gain, choice.price_priority), reverse=True
    )

    # Always seed one low-minutes cleanup and one high-demand incoming alongside
    # the raw top choices. This lets a useful second move survive beam pruning.
    seeds = list(ranked_singles[:seed_limit])
    health_threshold = float(strategy.get("squad_health_minutes_threshold", 25))
    health = next(
        (
            choice
            for choice in ranked_singles
            if expected_minutes(choice.transfer.player_out, strategy) < health_threshold
        ),
        None,
    )
    market = max(
        ranked_singles,
        key=lambda choice: (
            choice.transfer.player_in.transfers_in_event
            - choice.transfer.player_in.transfers_out_event,
            choice.gain,
        ),
        default=None,
    )
    for extra in (health, market):
        if extra is not None and all(
            item.transfer != extra.transfer for item in seeds
        ):
            seeds.append(extra)

    bundles: dict[tuple[tuple[int, int], ...], _TransferBundleChoice] = {}
    for first in seeds:
        proposed, next_bank, errors = apply_and_validate_transfers(
            owned, [first.transfer], settings.bank
        )
        if errors:
            continue
        next_owned = _owned_after_players(proposed, owned)
        next_settings = SquadSettings(
            entries=(),
            bank=next_bank,
            free_transfers=max(0, settings.free_transfers - 1),
            captain="",
            vice_captain="",
            chips={},
        )
        seconds = _transfer_choices(
            next_owned, candidates, scores, next_settings, strategy
        )
        seconds = [
            choice
            for choice in seconds
            if choice.transfer.player_out.id != first.transfer.player_in.id
            and choice.transfer.player_in.id != first.transfer.player_out.id
        ]
        seconds.sort(
            key=lambda choice: (choice.gain, choice.price_priority), reverse=True
        )
        for second in seconds[:second_limit]:
            transfers = (first.transfer, second.transfer)
            combined, _, combined_errors = apply_and_validate_transfers(
                owned, transfers, settings.bank
            )
            if combined_errors:
                continue
            gain = (
                _transfer_squad_objective(combined, scores, bench_weight) - baseline
            )
            key = tuple(
                sorted(
                    (transfer.player_out.id, transfer.player_in.id)
                    for transfer in transfers
                )
            )
            bundle = _TransferBundleChoice(
                gain=gain,
                price_priority=first.price_priority + second.price_priority,
                transfers=transfers,
                timing_notes=(*first.timing_notes, *second.timing_notes),
            )
            current = bundles.get(key)
            if current is None or (bundle.gain, bundle.price_priority) > (
                current.gain,
                current.price_priority,
            ):
                bundles[key] = bundle
    return sorted(
        bundles.values(),
        key=lambda bundle: (bundle.gain, bundle.price_priority),
        reverse=True,
    )


def _preferred_transfer_choice(
    choices: list[_TransferChoice], strategy: dict[str, Any]
) -> _TransferChoice | None:
    if not choices:
        return None
    best_gain = max(choice.gain for choice in choices)
    margin = max(0.0, float(strategy.get("price_change_tiebreak_gain_margin", 1.0)))
    near_best = [choice for choice in choices if choice.gain >= best_gain - margin]
    return max(near_best, key=lambda choice: (choice.price_priority, choice.gain))


def _choice_rationale(choice: _TransferChoice) -> str:
    transfer = choice.transfer
    text = (
        "The move improves the projected best XI plus weighted bench by "
        f"{choice.gain:.1f} over the configured horizon; incoming availability is "
        f"{availability(transfer.player_in)}%."
    )
    if choice.timing_notes:
        text += " Price timing: " + " ".join(choice.timing_notes)
    return text


def _transfer_option_id(transfers: Iterable[Transfer]) -> str:
    moves = tuple(transfers)
    if len(moves) == 1:
        move = moves[0]
        return f"transfer:{move.player_out.id}:{move.player_in.id}"
    return "transfers:" + "+".join(
        f"{move.player_out.id}:{move.player_in.id}" for move in moves
    )


def _transfer_action(transfers: Iterable[Transfer]) -> str:
    return ", ".join(
        f"{move.player_out.name} → {move.player_in.name}" for move in transfers
    )


def _bundle_rationale(bundle: _TransferBundleChoice) -> str:
    text = (
        "Together these moves improve the projected best XI plus weighted bench by "
        f"{bundle.gain:.1f} over the configured horizon."
    )
    if bundle.timing_notes:
        text += " Price timing: " + " ".join(dict.fromkeys(bundle.timing_notes))
    return text


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

    singles = _transfer_choices(owned, candidates, scores, settings, strategy)
    choice = _preferred_transfer_choice(singles, strategy)
    if choice is None:
        return []
    gain = choice.gain
    selected_transfers = (choice.transfer,)
    pairs = _pair_transfer_choices(
        owned, candidates, scores, settings, strategy, singles
    )
    if pairs:
        best_pair_gain = pairs[0].gain
        price_margin = max(
            0.0, float(strategy.get("price_change_tiebreak_gain_margin", 1.0))
        )
        near_best_pairs = [
            pair for pair in pairs if pair.gain >= best_pair_gain - price_margin
        ]
        best_pair = max(
            near_best_pairs,
            key=lambda pair: (pair.price_priority, pair.gain),
        )
        extra_gain_required = float(
            strategy.get("additional_free_transfer_min_gain", 4.0)
        )
        if best_pair.gain >= gain + extra_gain_required:
            gain = best_pair.gain
            selected_transfers = best_pair.transfers
    threshold = float(strategy.get("min_transfer_gain", 2.5))
    outgoing_is_unavailable = any(
        availability(transfer.player_out) < 75
        or transfer.player_out.status in {"i", "s", "u"}
        or not transfer.player_out.can_select
        for transfer in selected_transfers
    )
    if not outgoing_is_unavailable and bool(strategy.get("avoid_optional_transfers", True)):
        completed = int(strategy.get("completed_gameweeks", 0))
        minimum_sample = int(
            strategy.get("optional_transfer_min_completed_gameweeks", 2)
        )
        exception_gain = float(
            strategy.get("optional_transfer_exception_gain", threshold + 4.0)
        )
        if completed < minimum_sample or gain < exception_gain:
            return []
    if gain < threshold and all(
        availability(transfer.player_out) > 0 for transfer in selected_transfers
    ):
        return []
    return list(selected_transfers)


def _engine_options(
    owned: list[OwnedPlayer],
    candidates: list[Player],
    scores: dict[int, float],
    settings: SquadSettings,
    strategy: dict[str, Any],
    deterministic_transfers: list[Transfer],
) -> list[EngineOption]:
    """Expose hold plus the strongest legal transfer alternatives for review."""
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

    choices = _transfer_choices(owned, candidates, scores, settings, strategy)
    pair_choices = _pair_transfer_choices(
        owned, candidates, scores, settings, strategy, choices
    )
    choices.sort(key=lambda choice: (choice.gain, choice.price_priority), reverse=True)
    minimum_gain = float(strategy.get("min_transfer_gain", 2.5))
    horizon = max(1, int(strategy.get("fixture_horizon", 5)))
    maximum_gain = float(
        strategy.get("max_transfer_gain_per_gameweek", 4.0)
    ) * horizon
    limit = max(1, int(strategy.get("research_candidate_transfers", 3)))
    for choice in choices:
        gain, transfer = choice.gain, choice.transfer
        option_id = _transfer_option_id((transfer,))
        is_engine_pick = bool(
            len(deterministic_transfers) == 1
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
                rationale=_choice_rationale(choice),
                transfer=transfer,
            )
        )
        if len(options) - 1 >= limit:
            break

    pair_limit = max(0, int(strategy.get("research_pair_transfers", 2)))
    additional_gain = float(strategy.get("additional_free_transfer_min_gain", 4.0))
    best_single_gain = choices[0].gain if choices else 0.0
    if pair_limit:
        for bundle in (
            pair
            for pair in pair_choices
            if pair.gain >= best_single_gain + additional_gain
        ):
            option_id = _transfer_option_id(bundle.transfers)
            options.append(
                EngineOption(
                    id=option_id,
                    action=_transfer_action(bundle.transfers),
                    projected_gain=bundle.gain,
                    rationale=_bundle_rationale(bundle),
                    transfer=bundle.transfers[0],
                    additional_transfers=bundle.transfers[1:],
                )
            )
            if sum(bool(option.additional_transfers) for option in options) >= pair_limit:
                break
    if deterministic_transfers:
        option_id = _transfer_option_id(deterministic_transfers)
        if not any(option.id == option_id for option in options):
            if len(deterministic_transfers) == 1:
                transfer = deterministic_transfers[0]
                deterministic_choice = next(
                    (
                        item
                        for item in choices
                        if item.transfer.player_out.id == transfer.player_out.id
                        and item.transfer.player_in.id == transfer.player_in.id
                    ),
                    None,
                )
                gain = 0.0 if deterministic_choice is None else deterministic_choice.gain
                rationale = (
                    "The deterministic policy selected this legal whole-squad upgrade."
                    if deterministic_choice is None
                    else _choice_rationale(deterministic_choice)
                )
            else:
                bundle = next(
                    (
                        item
                        for item in pair_choices
                        if _transfer_option_id(item.transfers) == option_id
                    ),
                    None,
                )
                gain = 0.0 if bundle is None else bundle.gain
                rationale = (
                    "The deterministic policy selected this legal two-transfer upgrade."
                    if bundle is None
                    else _bundle_rationale(bundle)
                )
            options.append(
                EngineOption(
                    id=option_id,
                    action=_transfer_action(deterministic_transfers),
                    projected_gain=gain,
                    rationale=rationale,
                    transfer=deterministic_transfers[0],
                    additional_transfers=tuple(deterministic_transfers[1:]),
                )
            )

    def append_scouting_choice(choice: _TransferChoice, label: str) -> None:
        transfer = choice.transfer
        option_id = _transfer_option_id((transfer,))
        if any(option.id == option_id for option in options):
            return
        options.append(
            EngineOption(
                id=option_id,
                action=f"{transfer.player_out.name} → {transfer.player_in.name}",
                projected_gain=choice.gain,
                rationale=f"{_choice_rationale(choice)} {label}",
                transfer=transfer,
            )
        )

    health_limit = max(0, int(strategy.get("research_squad_health_transfers", 1)))
    health_minutes = float(strategy.get("squad_health_minutes_threshold", 25))
    health_choices = sorted(
        (
            choice
            for choice in choices
            if expected_minutes(choice.transfer.player_out, strategy) < health_minutes
            and choice.gain >= minimum_gain
        ),
        key=lambda choice: choice.gain,
        reverse=True,
    )
    for choice in health_choices[:health_limit]:
        append_scouting_choice(
            choice,
            "Squad-health candidate: it replaces a player projected below "
            f"{health_minutes:.0f} minutes.",
        )

    market_limit = max(0, int(strategy.get("research_market_momentum_transfers", 1)))
    market_minimum = float(strategy.get("market_momentum_min_gain", 1.0))
    best_by_incoming: dict[int, _TransferChoice] = {}
    for choice in choices:
        incoming_id = choice.transfer.player_in.id
        current = best_by_incoming.get(incoming_id)
        if current is None or choice.gain > current.gain:
            best_by_incoming[incoming_id] = choice
    market_choices = sorted(
        (
            choice
            for choice in best_by_incoming.values()
            if choice.gain >= market_minimum
            and choice.transfer.player_in.transfers_in_event
            > choice.transfer.player_in.transfers_out_event
        ),
        key=lambda choice: (
            choice.transfer.player_in.transfers_in_event
            - choice.transfer.player_in.transfers_out_event,
            choice.gain,
        ),
        reverse=True,
    )
    for choice in market_choices[:market_limit]:
        incoming = choice.transfer.player_in
        net_transfers = incoming.transfers_in_event - incoming.transfers_out_event
        append_scouting_choice(
            choice,
            f"Market-watch candidate: {incoming.name} has {net_transfers:,} net transfers "
            "in this Gameweek; that momentum does not add to the points projection.",
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
        for transfer in option.transfers:
            tracked[transfer.player_in.id] = transfer.player_in
            tracked[transfer.player_out.id] = transfer.player_out
            roles.setdefault(transfer.player_in.id, "transfer candidate")
            roles.setdefault(transfer.player_out.id, "transfer candidate")
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
        else _transfer_option_id(deterministic_transfers)
    )
    chosen_option_id = selected_option_id or default_option_id
    chosen_option = next(
        (option for option in engine_options if option.id == chosen_option_id), None
    )
    if chosen_option is None:
        raise ValueError(f"Unknown or non-shortlisted engine option {chosen_option_id!r}")
    transfers = list(chosen_option.transfers)
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
        count = len(transfers)
        moves = "; ".join(
            f"{transfer.player_out.name} to {transfer.player_in.name}"
            for transfer in transfers
        )
        transfer_text = (
            f"Use {count} free transfer{'s' if count != 1 else ''}: {moves}. "
            f"The moves remain within budget with £{remaining_bank / 10:.1f}m left "
            "and pass all squad rules."
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
    position_by_name: dict[str, str] = {}
    for entry in settings.entries:
        by_position[entry.position].append(entry.name)
        position_by_name[entry.name] = entry.position

    starting = [
        by_position["GK"][0],
        *by_position["DEF"][:4],
        *by_position["MID"][:4],
        *by_position["FWD"][:2],
    ]
    for protected in (settings.captain, settings.vice_captain):
        if protected in starting or protected not in position_by_name:
            continue
        position = position_by_name[protected]
        replaceable = next(
            (
                name for name in starting
                if position_by_name[name] == position
                and name not in {settings.captain, settings.vice_captain}
            ),
            None,
        )
        if replaceable is not None:
            starting[starting.index(replaceable)] = protected
    bench = [
        name for position in ("DEF", "MID", "FWD")
        for name in by_position[position] if name not in starting
    ]
    return Recommendation(
        event=event,
        transfers=[],
        points_hit=0,
        captain=settings.captain,
        vice_captain=settings.vice_captain,
        starting_xi=starting,
        bench=bench,
        reserve_goalkeeper=next(
            name for name in by_position["GK"] if name not in starting
        ),
        chip="None — save the chip",
        confidence="Low",
        explanation=(
            "Safe fallback: make no transfer and take no points hit because live inputs "
            f"could not be trusted ({reason}). Check late team news manually before the "
            "deadline; the configured captain and vice-captain start in a legal 4-4-2."
        ),
        source="fallback",
        fallback=True,
        validation=[
            "Fallback formation is 4-4-2",
            "Captain and vice-captain are starters",
            "No transfer or points hit proposed",
        ],
    )
