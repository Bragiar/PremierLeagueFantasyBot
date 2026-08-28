from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product
from typing import Any, Iterable

from fpl_bot.models import (
    ChipTarget,
    Event,
    GameweekPlan,
    OwnedPlayer,
    PlannedMove,
    Player,
    RollingPlan,
    SquadSettings,
    Transfer,
)
from fpl_bot.recommender import (
    _choose_lineup,
    _optimize_squad,
    _squad_objective,
    availability,
    fixture_difficulties,
    score_player,
    score_player_for_gameweek,
)
from fpl_bot.squad import apply_and_validate_transfers, selling_price


@dataclass(frozen=True)
class _PlannerState:
    owned: tuple[OwnedPlayer, ...]
    bank: int
    free_transfers: int
    objective: float
    weeks: tuple[GameweekPlan, ...]
    history: tuple[tuple[OwnedPlayer, ...], ...]


@dataclass(frozen=True)
class _ChipCandidate:
    event_id: int
    event_name: str
    uplift: float
    target_player: str | None
    rationale: str
    priority_score: float | None = None


def _chip_candidate_score(candidate: _ChipCandidate) -> float:
    return (
        candidate.uplift
        if candidate.priority_score is None
        else candidate.priority_score
    )


def _event_names(raw_events: Iterable[dict[str, Any]]) -> dict[int, str]:
    names: dict[int, str] = {}
    for raw in raw_events:
        try:
            event_id = int(raw["id"])
        except (KeyError, TypeError, ValueError):
            continue
        names[event_id] = str(raw.get("name") or f"Gameweek {event_id}")
    return names


def _future_projection_player(
    player: Player,
    event_id: int,
    current_event_id: int | None,
    *,
    games: int = 1,
) -> Player:
    if current_event_id is None or event_id <= current_event_id:
        return player
    price_floor = {"GK": 40, "DEF": 40, "MID": 45, "FWD": 45}[player.position]
    price_weight = {"GK": 0.08, "DEF": 0.10, "MID": 0.07, "FWD": 0.06}[
        player.position
    ]
    ceiling = {"GK": 5.0, "DEF": 5.5, "MID": 7.0, "FWD": 8.0}[player.position]
    price_prior = min(
        ceiling, 2.3 + max(0, player.cost - price_floor) * price_weight
    )
    observed = min(10.0, max(player.points_per_game, player.form, 2.0))
    sample_reliability = min(0.5, player.minutes / 900)
    time_weight = max(0.15, 1 - 0.12 * (event_id - current_event_id))
    observed_weight = sample_reliability * time_weight
    regressed_observed = (
        price_prior * (1 - observed_weight) + observed * observed_weight
    )
    return replace(
        player,
        expected_next=regressed_observed * max(1, games),
        form=regressed_observed,
        points_per_game=regressed_observed,
    )


def _scores_for_event(
    candidates: list[Player],
    fixtures: list[dict[str, Any]],
    event_id: int,
    strategy: dict[str, Any],
    *,
    current_event_id: int | None = None,
) -> dict[int, float]:
    difficulties = fixture_difficulties(fixtures, event_id, 1)

    return {
        player.id: score_player_for_gameweek(
            _future_projection_player(
                player,
                event_id,
                current_event_id,
                games=len(difficulties.get(player.team_id, [])),
            ),
            difficulties.get(player.team_id, []),
            strategy,
        )
        for player in candidates
    }


def _owned_from_players(
    players: Iterable[Player], previous: Iterable[OwnedPlayer]
) -> tuple[OwnedPlayer, ...]:
    purchase_prices = {item.player.id: item.purchase_price for item in previous}
    return tuple(
        OwnedPlayer(player, purchase_prices.get(player.id, player.cost))
        for player in players
    )


def _apply(
    owned: tuple[OwnedPlayer, ...], bank: int, transfers: tuple[Transfer, ...]
) -> tuple[tuple[OwnedPlayer, ...], int] | None:
    players, remaining_bank, errors = apply_and_validate_transfers(
        owned, transfers, bank
    )
    if errors:
        return None
    return _owned_from_players(players, owned), remaining_bank


def _next_free_transfers(
    before: int, transfers_used: int, chip_id: str, cap: int
) -> int:
    if chip_id in {"chip:wildcard", "chip:free_hit"}:
        return before
    return min(cap, max(0, before - transfers_used) + 1)


def _planned_moves(transfers: Iterable[Transfer]) -> tuple[PlannedMove, ...]:
    return tuple(
        PlannedMove(
            player_out_id=transfer.player_out.id,
            player_out=transfer.player_out.name,
            player_in_id=transfer.player_in.id,
            player_in=transfer.player_in.name,
        )
        for transfer in transfers
    )


def _project_week(
    players: list[Player],
    scores: dict[int, float],
    *,
    chip_id: str = "chip:none",
    preferred_captain: str | None = None,
) -> tuple[float, list[Player], list[Player], Player, Player]:
    lineup, bench, reserve_goalkeeper = _choose_lineup(players, scores)
    captain = max(
        lineup,
        key=lambda player: (
            scores[player.id]
            + player.cost / 50
            + 0.02 * player.selected_by_percent
        ),
    )
    if preferred_captain:
        preferred = next(
            (player for player in lineup if player.name == preferred_captain), None
        )
        if preferred is not None:
            captain = preferred
    projected = sum(scores[player.id] for player in lineup) + scores[captain.id]
    if chip_id == "chip:triple_captain":
        projected += scores[captain.id]
    elif chip_id == "chip:bench_boost":
        projected += sum(scores[player.id] for player in bench)
        projected += scores[reserve_goalkeeper.id]
    return projected, lineup, bench, reserve_goalkeeper, captain


def _candidate_pool(
    candidates: list[Player],
    lookahead_scores: dict[int, float],
    strategy: dict[str, Any],
) -> dict[str, list[Player]]:
    per_position = max(4, int(strategy.get("planner_candidates_per_position", 10)))
    pools: dict[str, list[Player]] = {}
    for position in ("GK", "DEF", "MID", "FWD"):
        eligible = [
            player
            for player in candidates
            if player.position == position
            and player.can_select
            and player.cost > 0
            and availability(player) >= 90
        ]
        strongest = sorted(
            eligible, key=lambda player: lookahead_scores[player.id], reverse=True
        )[:per_position]
        cheapest = sorted(
            eligible, key=lambda player: (player.cost, -lookahead_scores[player.id])
        )[:4]
        pools[position] = list({player.id: player for player in [*strongest, *cheapest]}.values())
    return pools


def _single_transfer_candidates(
    owned: tuple[OwnedPlayer, ...],
    bank: int,
    candidates: list[Player],
    lookahead_scores: dict[int, float],
    strategy: dict[str, Any],
    *,
    excluded_out_ids: frozenset[int] = frozenset(),
) -> list[tuple[float, Transfer]]:
    current_ids = {item.player.id for item in owned}
    risky = [item for item in owned if availability(item.player) < 75]
    outgoing_limit = max(2, int(strategy.get("planner_outgoing_candidates", 4)))
    weakest = sorted(owned, key=lambda item: lookahead_scores[item.player.id])[
        :outgoing_limit
    ]
    outgoing_pool = list(
        {
            item.player.id: item
            for item in [*risky, *weakest]
            if item.player.id not in excluded_out_ids
        }.values()
    )
    pools = _candidate_pool(candidates, lookahead_scores, strategy)
    minimum_gain = float(strategy.get("planner_min_transfer_gain", 0.75))
    choices: list[tuple[float, Transfer]] = []
    for outgoing in outgoing_pool:
        sale = selling_price(outgoing.player.cost, outgoing.purchase_price)
        funds = bank + sale
        for incoming in pools[outgoing.player.position]:
            if incoming.id in current_ids or incoming.cost > funds:
                continue
            transfer = Transfer(
                player_out=outgoing.player,
                player_in=incoming,
                selling_price=sale,
                buying_price=incoming.cost,
            )
            if _apply(owned, bank, (transfer,)) is None:
                continue
            gain = lookahead_scores[incoming.id] - lookahead_scores[outgoing.player.id]
            if gain < minimum_gain and availability(outgoing.player) > 0:
                continue
            choices.append((gain, transfer))
    choices.sort(key=lambda item: item[0], reverse=True)
    limit = max(2, int(strategy.get("planner_transfer_options_per_state", 8)))
    return choices[:limit]


def _actions_for_state(
    state: _PlannerState,
    candidates: list[Player],
    lookahead_scores: dict[int, float],
    strategy: dict[str, Any],
) -> list[tuple[Transfer, ...]]:
    actions: list[tuple[Transfer, ...]] = [()]
    allowed_hits = max(0, int(strategy.get("max_points_hit", 0))) // 4
    max_transfers = min(
        max(1, int(strategy.get("planner_max_transfers_per_week", 2))),
        state.free_transfers + allowed_hits,
    )
    if max_transfers < 1:
        return actions

    singles = _single_transfer_candidates(
        state.owned, state.bank, candidates, lookahead_scores, strategy
    )
    actions.extend((transfer,) for _, transfer in singles)
    if max_transfers < 2:
        return actions

    pair_choices: list[tuple[float, tuple[Transfer, Transfer]]] = []
    pair_seeds = max(2, int(strategy.get("planner_pair_seeds", 5)))
    for first_gain, first in singles[:pair_seeds]:
        applied = _apply(state.owned, state.bank, (first,))
        if applied is None:
            continue
        next_owned, next_bank = applied
        seconds = _single_transfer_candidates(
            next_owned,
            next_bank,
            candidates,
            lookahead_scores,
            strategy,
            excluded_out_ids=frozenset({first.player_in.id}),
        )
        for second_gain, second in seconds[:pair_seeds]:
            transfers = (first, second)
            if _apply(state.owned, state.bank, transfers) is None:
                continue
            pair_choices.append((first_gain + second_gain, transfers))
    pair_choices.sort(key=lambda item: item[0], reverse=True)
    actions.extend(transfers for _, transfers in pair_choices[:pair_seeds])
    return actions


def _state_signature(state: _PlannerState) -> tuple[tuple[int, ...], int, int]:
    return (
        tuple(sorted(item.player.id for item in state.owned)),
        state.bank,
        state.free_transfers,
    )


def _confidence(offset: int) -> str:
    if offset == 0:
        return "High"
    if offset <= 2:
        return "Medium"
    return "Low"


def _chip_name(chip_id: str) -> str:
    return {
        "chip:none": "None",
        "chip:triple_captain": "Triple Captain",
        "chip:bench_boost": "Bench Boost",
        "chip:free_hit": "Free Hit",
        "chip:wildcard": "Wildcard",
    }.get(chip_id, chip_id)


def _rough_best_squad_score(
    candidates: list[Player], scores: dict[int, float]
) -> float:
    quotas = {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}
    selected: list[Player] = []
    for position, quota in quotas.items():
        selected.extend(
            sorted(
                (player for player in candidates if player.position == position),
                key=lambda player: scores[player.id],
                reverse=True,
            )[:quota]
        )
    if len(selected) != 15:
        return 0.0
    return _squad_objective(selected, scores, 0.1)


def _long_horizon_scores(
    candidates: list[Player],
    fixtures: list[dict[str, Any]],
    event_id: int,
    horizon: int,
    strategy: dict[str, Any],
    *,
    current_event_id: int,
) -> dict[int, float]:
    difficulties = fixture_difficulties(fixtures, event_id, horizon)

    return {
        player.id: score_player(
            _future_projection_player(player, event_id, current_event_id),
            difficulties.get(player.team_id, []),
            strategy,
        )
        for player in candidates
    }


def _assign_chip_windows(
    candidate_map: dict[str, list[_ChipCandidate]],
    selected_chip_id: str,
    current_event: int,
) -> dict[str, _ChipCandidate]:
    chip_ids = [chip_id for chip_id, values in candidate_map.items() if values]
    if not chip_ids:
        return {}
    thresholds = {
        "chip:triple_captain": 12.0,
        "chip:bench_boost": 20.0,
        "chip:free_hit": 25.0,
        "chip:wildcard": 35.0,
    }
    shortlists: list[list[_ChipCandidate]] = []
    for chip_id in chip_ids:
        ranked = sorted(
            candidate_map[chip_id],
            key=lambda item: (_chip_candidate_score(item), -item.event_id),
            reverse=True,
        )
        if chip_id == selected_chip_id and selected_chip_id != "chip:none":
            current = [item for item in ranked if item.event_id == current_event]
            shortlists.append(current[:1] or ranked[:1])
        else:
            shortlists.append(ranked[:5])

    best_score = float("-inf")
    best: tuple[_ChipCandidate, ...] | None = None
    for combination in product(*shortlists):
        event_ids = [item.event_id for item in combination]
        if len(event_ids) != len(set(event_ids)):
            continue
        score = sum(
            _chip_candidate_score(item) / thresholds[chip_id]
            for chip_id, item in zip(chip_ids, combination, strict=True)
        )
        by_chip = dict(zip(chip_ids, combination, strict=True))
        for left_index, left in enumerate(combination):
            for right in combination[left_index + 1 :]:
                if abs(left.event_id - right.event_id) == 1:
                    score -= 0.12
        wildcard = by_chip.get("chip:wildcard")
        bench_boost = by_chip.get("chip:bench_boost")
        free_hit = by_chip.get("chip:free_hit")
        if wildcard and bench_boost and 1 <= bench_boost.event_id - wildcard.event_id <= 3:
            score += 0.15
        if wildcard and free_hit and 1 <= free_hit.event_id - wildcard.event_id <= 2:
            score -= 0.35
        if score > best_score:
            best_score = score
            best = combination
    if best is None:
        return {}
    return dict(zip(chip_ids, best, strict=True))


def _build_chip_targets(
    current_event: Event,
    raw_events: list[dict[str, Any]],
    fixtures: list[dict[str, Any]],
    candidates: list[Player],
    settings: SquadSettings,
    strategy: dict[str, Any],
    selected_chip_id: str,
    selected_chip_uplift: float,
    route_squads: dict[int, tuple[OwnedPlayer, ...]],
    route_banks: dict[int, int],
) -> tuple[ChipTarget, ...]:
    half = "first_half" if current_event.id <= 19 else "second_half"
    expiry = 19 if current_event.id <= 19 else 38
    available = {
        f"chip:{chip}"
        for chip, status in settings.chips.get(half, {}).items()
        if status == "available"
    }
    if not available:
        return ()

    names = _event_names(raw_events)
    event_ids = [
        event_id
        for event_id in range(current_event.id, expiry + 1)
        if any(fixture.get("event") == event_id for fixture in fixtures)
    ]
    if not event_ids:
        return ()
    final_owned = route_squads[max(route_squads)]
    final_bank = route_banks[max(route_banks)]
    score_cache = {
        event_id: _scores_for_event(
            candidates,
            fixtures,
            event_id,
            strategy,
            current_event_id=current_event.id,
        )
        for event_id in event_ids
    }
    candidate_map: dict[str, list[_ChipCandidate]] = {
        chip_id: [] for chip_id in available
    }
    fh_proxy: list[tuple[float, int, tuple[OwnedPlayer, ...], int]] = []
    wc_proxy: list[
        tuple[float, int, tuple[OwnedPlayer, ...], int, dict[int, float]]
    ] = []
    planning_horizon = min(
        int(strategy.get("fixture_horizon", 5)),
        int(strategy.get("max_fixture_horizon", 6)),
    )
    rolling_end = current_event.id + planning_horizon - 1
    promoted_teams = {
        str(name).strip().lower()
        for name in strategy.get("promoted_teams", [])
        if str(name).strip()
    }
    team_names = {player.team_id: player.team_name for player in candidates}

    for event_id in event_ids:
        owned = route_squads.get(event_id, final_owned)
        bank = route_banks.get(event_id, final_bank)
        players = [item.player for item in owned]
        scores = score_cache[event_id]
        projected, lineup, bench, reserve, captain = _project_week(players, scores)
        del projected
        if "chip:triple_captain" in available and (
            event_id > current_event.id or selected_chip_id == "chip:triple_captain"
        ):
            promoted_home = any(
                fixture.get("event") == event_id
                and int(fixture.get("team_h", 0)) == captain.team_id
                and team_names.get(int(fixture.get("team_a", 0)), "").lower()
                in promoted_teams
                for fixture in fixtures
            )
            tc_bonus = (
                float(strategy.get("planner_promoted_home_tc_bonus", 2.5))
                if promoted_home
                else 0.0
            )
            candidate_map["chip:triple_captain"].append(
                _ChipCandidate(
                    event_id,
                    names.get(event_id, f"Gameweek {event_id}"),
                    scores[captain.id],
                    captain.name,
                    (
                        f"One extra copy of {captain.name}'s captain projection"
                        + (" in a home fixture against a promoted club." if promoted_home else ".")
                    ),
                    scores[captain.id] + tc_bonus,
                )
            )
        if "chip:bench_boost" in available and (
            event_id > current_event.id or selected_chip_id == "chip:bench_boost"
        ):
            bench_uplift = sum(scores[player.id] for player in bench) + scores[reserve.id]
            candidate_map["chip:bench_boost"].append(
                _ChipCandidate(
                    event_id,
                    names.get(event_id, f"Gameweek {event_id}"),
                    bench_uplift,
                    None,
                    "Projected points from the four substitutes in the route squad.",
                )
            )

        team_value = bank + sum(
            selling_price(item.player.cost, item.purchase_price) for item in owned
        )
        if (
            "chip:free_hit" in available
            and event_id != 1
            and (event_id > current_event.id or selected_chip_id == "chip:free_hit")
        ):
            difficulties = fixture_difficulties(fixtures, event_id, 1)
            blank_players = sum(
                1 for player in players if not difficulties.get(player.team_id)
            )
            baseline = _squad_objective(players, scores, 0.0)
            proxy = max(0.0, _rough_best_squad_score(candidates, scores) - baseline)
            fh_proxy.append((proxy + blank_players * 6.0, event_id, owned, team_value))
        if (
            "chip:wildcard" in available
            and event_id != 1
            and (event_id > current_event.id or selected_chip_id == "chip:wildcard")
            and event_id <= rolling_end
        ):
            horizon = min(planning_horizon, expiry - event_id + 1)
            horizon_scores = _long_horizon_scores(
                candidates,
                fixtures,
                event_id,
                horizon,
                strategy,
                current_event_id=current_event.id,
            )
            baseline = _squad_objective(players, horizon_scores, 0.15)
            proxy = max(
                0.0, _rough_best_squad_score(candidates, horizon_scores) - baseline
            )
            wc_proxy.append((proxy, event_id, owned, team_value, horizon_scores))

    searches = max(2, int(strategy.get("planner_chip_window_searches", 4)))
    if "chip:free_hit" in available:
        fh_search = sorted(fh_proxy, reverse=True)[:searches]
        if selected_chip_id == "chip:free_hit":
            current = [item for item in fh_proxy if item[1] == current_event.id]
            if current and all(item[1] != current_event.id for item in fh_search):
                fh_search[-1:] = current[:1]
        for _, event_id, owned, team_value in fh_search:
            scores = score_cache[event_id]
            players = [item.player for item in owned]
            try:
                optimized_squad, optimized = _optimize_squad(
                    candidates, scores, team_value, bench_weight=0.0
                )
                del optimized_squad
                baseline = _squad_objective(players, scores, 0.0)
                uplift = max(0.0, optimized - baseline)
            except ValueError:
                uplift = 0.0
            candidate_map["chip:free_hit"].append(
                _ChipCandidate(
                    event_id,
                    names.get(event_id, f"Gameweek {event_id}"),
                    uplift,
                    None,
                    (
                        "One-Gameweek optimized squad compared with the planned route squad."
                        + (
                            " GW19 carries an opportunity cost because a first-half Free Hit "
                            "there prevents another Free Hit in GW20."
                            if event_id == 19 and current_event.id <= 19
                            else ""
                        )
                    ),
                    (
                        max(
                            0.0,
                            uplift
                            - float(
                                strategy.get("planner_gw19_free_hit_penalty", 5.0)
                            ),
                        )
                        if event_id == 19 and current_event.id <= 19
                        else uplift
                    ),
                )
            )
    if "chip:wildcard" in available:
        wc_search = sorted(
            wc_proxy, key=lambda item: item[0], reverse=True
        )[:searches]
        if selected_chip_id == "chip:wildcard":
            current = [item for item in wc_proxy if item[1] == current_event.id]
            if current and all(item[1] != current_event.id for item in wc_search):
                wc_search[-1:] = current[:1]
        for _, event_id, owned, team_value, horizon_scores in wc_search:
            players = [item.player for item in owned]
            try:
                optimized_squad, optimized = _optimize_squad(
                    candidates, horizon_scores, team_value, bench_weight=0.15
                )
                del optimized_squad
                baseline = _squad_objective(players, horizon_scores, 0.15)
                uplift = max(0.0, optimized - baseline)
            except ValueError:
                uplift = 0.0
            candidate_map["chip:wildcard"].append(
                _ChipCandidate(
                    event_id,
                    names.get(event_id, f"Gameweek {event_id}"),
                    uplift,
                    None,
                    f"Permanent optimized squad across the next {planning_horizon} Gameweeks.",
                )
            )

    if selected_chip_id in candidate_map and selected_chip_id != "chip:none":
        candidate_map[selected_chip_id] = [
            replace(item, uplift=selected_chip_uplift)
            if item.event_id == current_event.id
            else item
            for item in candidate_map[selected_chip_id]
        ]
    assigned = _assign_chip_windows(candidate_map, selected_chip_id, current_event.id)
    thresholds = {
        "chip:triple_captain": float(
            strategy.get("triple_captain_exceptional_uplift", 12)
        ),
        "chip:bench_boost": float(strategy.get("bench_boost_exceptional_uplift", 20)),
        "chip:free_hit": float(strategy.get("free_hit_exceptional_uplift", 25)),
        "chip:wildcard": float(strategy.get("wildcard_exceptional_uplift", 35)),
    }
    labels = {
        "chip:triple_captain": "Triple Captain",
        "chip:bench_boost": "Bench Boost",
        "chip:free_hit": "Free Hit",
        "chip:wildcard": "Wildcard",
    }
    targets: list[ChipTarget] = []
    used_primary_events = {item.event_id for item in assigned.values()}
    rolling_end = current_event.id + planning_horizon - 1
    for chip_id in (
        "chip:wildcard",
        "chip:free_hit",
        "chip:bench_boost",
        "chip:triple_captain",
    ):
        if chip_id not in available or chip_id not in assigned:
            continue
        primary = assigned[chip_id]
        backups = sorted(
            (
                item
                for item in candidate_map[chip_id]
                if item.event_id != primary.event_id
                and item.event_id not in used_primary_events
            ),
            key=lambda item: (_chip_candidate_score(item), -item.event_id),
            reverse=True,
        )
        backup = backups[0] if backups else None
        ratio = primary.uplift / max(0.1, thresholds[chip_id])
        confidence = (
            "Medium"
            if primary.event_id <= rolling_end and ratio >= 0.65
            else "Low"
        )
        if chip_id == selected_chip_id and primary.event_id == current_event.id:
            confidence = "High"
        targets.append(
            ChipTarget(
                chip_id=chip_id,
                chip=labels[chip_id],
                primary_event_id=primary.event_id,
                primary_event_name=primary.event_name,
                backup_event_id=None if backup is None else backup.event_id,
                backup_event_name="None" if backup is None else backup.event_name,
                target_player=primary.target_player,
                projected_uplift=primary.uplift,
                confidence=confidence,
                rationale=primary.rationale,
            )
        )
    return tuple(targets)


def build_rolling_plan(
    event: Event,
    raw_events: list[dict[str, Any]],
    owned: list[OwnedPlayer],
    current_squad: list[Player],
    candidates: list[Player],
    fixtures: list[dict[str, Any]],
    settings: SquadSettings,
    strategy: dict[str, Any],
    immediate_transfers: list[Transfer],
    selected_chip_id: str,
    current_captain: str,
    selected_chip_uplift: float = 0.0,
) -> RollingPlan:
    """Plan a legal, reachable route and provisional chip windows."""
    names = _event_names(raw_events)
    horizon = min(
        int(strategy.get("fixture_horizon", 5)),
        int(strategy.get("max_fixture_horizon", 6)),
    )
    event_ids = list(range(event.id, min(38, event.id + horizon - 1) + 1))
    score_strategy = dict(strategy)
    score_strategy["season_started"] = event.id > 1
    score_cache = {
        event_id: _scores_for_event(
            candidates,
            fixtures,
            event_id,
            score_strategy,
            current_event_id=event.id,
        )
        for event_id in event_ids
    }
    free_transfer_cap = max(1, int(strategy.get("planner_free_transfer_cap", 5)))
    transfer_penalty = float(strategy.get("planner_transfer_uncertainty_cost", 0.6))
    saved_transfer_value = float(strategy.get("planner_saved_transfer_value", 0.8))
    bench_weight = float(strategy.get("planner_bench_weight", 0.08))

    original_owned = tuple(owned)
    if selected_chip_id == "chip:free_hit":
        persistent_owned = original_owned
        current_bank = settings.bank
    elif selected_chip_id == "chip:wildcard":
        persistent_owned = _owned_from_players(current_squad, original_owned)
        team_value = settings.bank + sum(
            selling_price(item.player.cost, item.purchase_price) for item in original_owned
        )
        current_bank = team_value - sum(player.cost for player in current_squad)
    else:
        applied = _apply(original_owned, settings.bank, tuple(immediate_transfers))
        if applied is None:
            raise ValueError("Could not initialize rolling plan from the selected transfer")
        persistent_owned, current_bank = applied

    transfer_count = len(immediate_transfers)
    current_hit = max(0, transfer_count - settings.free_transfers) * 4
    current_free_after = _next_free_transfers(
        settings.free_transfers,
        transfer_count,
        selected_chip_id,
        free_transfer_cap,
    )
    current_scores = score_cache[event.id]
    projected, lineup, bench, reserve, projected_captain = _project_week(
        current_squad,
        current_scores,
        chip_id=selected_chip_id,
        preferred_captain=current_captain,
    )
    current_week = GameweekPlan(
        event_id=event.id,
        event_name=names.get(event.id, event.name),
        transfers=_planned_moves(immediate_transfers),
        chip=_chip_name(selected_chip_id),
        captain=projected_captain.name,
        starting_xi=tuple(player.name for player in lineup),
        bench=tuple(player.name for player in bench),
        reserve_goalkeeper=reserve.name,
        projected_score=round(projected - current_hit, 2),
        points_hit=current_hit,
        free_transfers_before=settings.free_transfers,
        free_transfers_after=current_free_after,
        bank_after=round(current_bank / 10, 1),
        confidence="High",
        rationale="Current reviewed action; later weeks are optimized from this legal state.",
    )
    state = _PlannerState(
        owned=persistent_owned,
        bank=current_bank,
        free_transfers=current_free_after,
        objective=projected - current_hit - transfer_penalty * transfer_count,
        weeks=(current_week,),
        history=(persistent_owned,),
    )
    beam = [state]
    beam_width = max(5, int(strategy.get("planner_beam_width", 35)))

    for offset, event_id in enumerate(event_ids[1:], start=1):
        remaining_ids = event_ids[offset:]
        lookahead_scores = {
            player.id: sum(score_cache[item][player.id] for item in remaining_ids)
            for player in candidates
        }
        expanded: dict[tuple[tuple[int, ...], int, int], _PlannerState] = {}
        for current in beam:
            for transfers in _actions_for_state(
                current, candidates, lookahead_scores, score_strategy
            ):
                applied = _apply(current.owned, current.bank, transfers)
                if applied is None:
                    continue
                next_owned, next_bank = applied
                transfer_count = len(transfers)
                hit = max(0, transfer_count - current.free_transfers) * 4
                next_free = _next_free_transfers(
                    current.free_transfers,
                    transfer_count,
                    "chip:none",
                    free_transfer_cap,
                )
                players = [item.player for item in next_owned]
                projected, lineup, bench, reserve, captain = _project_week(
                    players, score_cache[event_id]
                )
                bench_value = (
                    sum(score_cache[event_id][player.id] for player in bench)
                    + score_cache[event_id][reserve.id]
                )
                rationale = (
                    "Roll to preserve transfer flexibility."
                    if not transfers
                    else (
                        "Conditional route: the moves improve remaining-horizon player "
                        f"ratings by {sum(lookahead_scores[transfer.player_in.id] - lookahead_scores[transfer.player_out.id] for transfer in transfers):.1f}."
                    )
                )
                week = GameweekPlan(
                    event_id=event_id,
                    event_name=names.get(event_id, f"Gameweek {event_id}"),
                    transfers=_planned_moves(transfers),
                    chip="None",
                    captain=captain.name,
                    starting_xi=tuple(player.name for player in lineup),
                    bench=tuple(player.name for player in bench),
                    reserve_goalkeeper=reserve.name,
                    projected_score=round(projected - hit, 2),
                    points_hit=hit,
                    free_transfers_before=current.free_transfers,
                    free_transfers_after=next_free,
                    bank_after=round(next_bank / 10, 1),
                    confidence=_confidence(offset),
                    rationale=rationale,
                )
                candidate_state = _PlannerState(
                    owned=next_owned,
                    bank=next_bank,
                    free_transfers=next_free,
                    objective=(
                        current.objective
                        + projected
                        + bench_weight * bench_value
                        - hit
                        - transfer_penalty * transfer_count
                    ),
                    weeks=(*current.weeks, week),
                    history=(*current.history, next_owned),
                )
                signature = _state_signature(candidate_state)
                existing = expanded.get(signature)
                if existing is None or candidate_state.objective > existing.objective:
                    expanded[signature] = candidate_state
        if not expanded:
            break
        beam = sorted(
            expanded.values(),
            key=lambda item: item.objective + saved_transfer_value * item.free_transfers,
            reverse=True,
        )[:beam_width]

    best = max(
        beam,
        key=lambda item: item.objective + saved_transfer_value * item.free_transfers,
    )
    route_squads = {
        week.event_id: squad for week, squad in zip(best.weeks, best.history, strict=True)
    }
    route_banks = {
        week.event_id: int(round(week.bank_after * 10)) for week in best.weeks
    }
    chip_targets = _build_chip_targets(
        event,
        raw_events,
        fixtures,
        candidates,
        settings,
        score_strategy,
        selected_chip_id,
        selected_chip_uplift,
        route_squads,
        route_banks,
    )
    return RollingPlan(
        generated_for_event=event.id,
        horizon=len(best.weeks),
        total_projected_score=round(
            sum(week.projected_score for week in best.weeks), 2
        ),
        gameweeks=best.weeks,
        chip_targets=chip_targets,
    )


def with_plan_changes(
    plan: RollingPlan, previous: dict[str, Any] | None
) -> RollingPlan:
    if not previous or not isinstance(previous.get("gameweeks"), list):
        return replace(plan, changes=("Created the first saved rolling plan.",))

    changes: list[str] = []
    previous_event = previous.get("generated_for_event")
    if isinstance(previous_event, int) and previous_event != plan.generated_for_event:
        changes.append(
            f"Advanced the rolling plan from GW{previous_event} to GW{plan.generated_for_event}."
        )
    previous_weeks = {
        int(week["event_id"]): week
        for week in previous.get("gameweeks", [])
        if isinstance(week, dict) and isinstance(week.get("event_id"), int)
    }
    for week in plan.gameweeks:
        old = previous_weeks.get(week.event_id)
        if old is None:
            continue
        old_action = str(old.get("action") or "Roll / no transfer")
        if old_action != week.action:
            changes.append(
                f"GW{week.event_id} transfer plan changed: {old_action} → {week.action}."
            )
        old_captain = str(old.get("captain") or "")
        if old_captain and old_captain != week.captain:
            changes.append(
                f"GW{week.event_id} captain changed: {old_captain} → {week.captain}."
            )

    previous_targets = {
        str(item.get("chip_id")): item
        for item in previous.get("chip_targets", [])
        if isinstance(item, dict)
    }
    for target in plan.chip_targets:
        old = previous_targets.get(target.chip_id)
        if old is None:
            continue
        old_event = old.get("primary_event_id")
        if old_event != target.primary_event_id:
            changes.append(
                f"{target.chip} target changed: GW{old_event} → GW{target.primary_event_id}."
            )
    if not changes:
        changes.append("No material transfer, captain or chip-window changes since the saved plan.")
    return replace(plan, changes=tuple(changes[:10]))
