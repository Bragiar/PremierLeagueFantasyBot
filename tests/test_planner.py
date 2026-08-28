from dataclasses import replace
from datetime import UTC, datetime

from fpl_bot.models import (
    Event,
    GameweekPlan,
    OwnedPlayer,
    RollingPlan,
    SquadEntry,
    SquadSettings,
)
from fpl_bot.planner import (
    _ChipCandidate,
    _assign_chip_windows,
    _future_projection_player,
    _next_free_transfers,
    build_rolling_plan,
    with_plan_changes,
)


def planner_strategy():
    return {
        "fixture_horizon": 3,
        "max_fixture_horizon": 3,
        "fixture_weight": 0.45,
        "form_weight": 0.8,
        "ownership_weight": 0.08,
        "secure_starter_weight": 1.6,
        "defensive_contribution_weight": 0.35,
        "lineup_fixture_weight": 1.0,
        "lineup_form_weight": 0.25,
        "lineup_ownership_weight": 0.02,
        "lineup_secure_starter_weight": 1.6,
        "lineup_defensive_contribution_weight": 0.2,
        "planner_free_transfer_cap": 5,
        "planner_max_transfers_per_week": 2,
        "planner_beam_width": 8,
        "planner_candidates_per_position": 4,
        "planner_outgoing_candidates": 2,
        "planner_transfer_options_per_state": 3,
        "planner_pair_seeds": 2,
        "planner_min_transfer_gain": 2.0,
        "planner_transfer_uncertainty_cost": 1.0,
        "planner_saved_transfer_value": 0.8,
        "planner_chip_window_searches": 2,
        "max_points_hit": 0,
    }


def test_free_transfers_roll_to_five_and_chips_preserve_the_bank():
    assert _next_free_transfers(4, 0, "chip:none", 5) == 5
    assert _next_free_transfers(5, 0, "chip:none", 5) == 5
    assert _next_free_transfers(3, 2, "chip:none", 5) == 2
    assert _next_free_transfers(3, 0, "chip:wildcard", 5) == 3
    assert _next_free_transfers(2, 0, "chip:free_hit", 5) == 2


def test_current_form_decays_toward_a_stable_future_prior(make_player):
    player = replace(
        make_player(1, "FWD", 1, cost=75),
        form=10,
        points_per_game=10,
        minutes=90,
    )

    near = _future_projection_player(player, 3, 2)
    distant = _future_projection_player(player, 12, 2)

    assert distant.form < near.form
    assert distant.expected_next < near.expected_next


def test_rolling_plan_carries_a_legal_route_and_bank_forward(legal_players):
    settings = SquadSettings(
        entries=tuple(
            SquadEntry(player.name, player.position, player.cost)
            for player in legal_players
        ),
        bank=0,
        free_transfers=1,
        captain=legal_players[-1].name,
        vice_captain=legal_players[-2].name,
        chips={
            half: {
                chip: "used"
                for chip in ("wildcard", "free_hit", "bench_boost", "triple_captain")
            }
            for half in ("first_half", "second_half")
        },
    )
    event = Event(2, "Gameweek 2", datetime(2026, 8, 28, 17, 30, tzinfo=UTC))
    raw_events = [{"id": event_id, "name": f"Gameweek {event_id}"} for event_id in range(2, 5)]
    fixtures = []
    for event_id in range(2, 5):
        for team_id in range(1, 7, 2):
            fixtures.append(
                {
                    "event": event_id,
                    "finished": False,
                    "team_h": team_id,
                    "team_a": team_id + 1,
                    "team_h_difficulty": 3,
                    "team_a_difficulty": 3,
                }
            )

    plan = build_rolling_plan(
        event,
        raw_events,
        [OwnedPlayer(player, player.cost) for player in legal_players],
        legal_players,
        legal_players,
        fixtures,
        settings,
        planner_strategy(),
        [],
        "chip:none",
        legal_players[-1].name,
    )

    assert plan.horizon == 3
    assert plan.gameweeks[0].free_transfers_after == 2
    assert all(week.points_hit == 0 for week in plan.gameweeks)
    assert all(len(week.starting_xi) == 11 for week in plan.gameweeks)
    assert all(len(week.bench) == 3 for week in plan.gameweeks)
    assert plan.chip_targets == ()


def test_chip_calendar_never_assigns_two_chips_to_one_gameweek():
    candidate_map = {
        "chip:triple_captain": [
            _ChipCandidate(3, "Gameweek 3", 12, "Haaland", "Captain"),
            _ChipCandidate(4, "Gameweek 4", 11, "Palmer", "Captain"),
        ],
        "chip:bench_boost": [
            _ChipCandidate(3, "Gameweek 3", 20, None, "Bench"),
            _ChipCandidate(5, "Gameweek 5", 18, None, "Bench"),
        ],
    }

    assigned = _assign_chip_windows(candidate_map, "chip:none", 2)

    assert len({item.event_id for item in assigned.values()}) == len(assigned)


def test_chip_calendar_avoids_free_hit_immediately_after_wildcard():
    candidate_map = {
        "chip:wildcard": [
            _ChipCandidate(3, "Gameweek 3", 35, None, "Wildcard"),
            _ChipCandidate(5, "Gameweek 5", 34, None, "Wildcard"),
        ],
        "chip:free_hit": [
            _ChipCandidate(4, "Gameweek 4", 25, None, "Free Hit"),
            _ChipCandidate(10, "Gameweek 10", 24, None, "Free Hit"),
        ],
    }

    assigned = _assign_chip_windows(candidate_map, "chip:none", 2)

    wildcard = assigned["chip:wildcard"].event_id
    free_hit = assigned["chip:free_hit"].event_id
    assert not 1 <= free_hit - wildcard <= 2


def test_plan_change_log_reports_material_route_change():
    week = GameweekPlan(
        event_id=3,
        event_name="Gameweek 3",
        transfers=(),
        chip="None",
        captain="Haaland",
        starting_xi=(),
        bench=(),
        reserve_goalkeeper="Keeper",
        projected_score=70,
        points_hit=0,
        free_transfers_before=2,
        free_transfers_after=3,
        bank_after=0,
        confidence="Medium",
        rationale="Roll",
    )
    plan = RollingPlan(2, 1, 70, (week,), ())
    previous = {
        "generated_for_event": 2,
        "gameweeks": [
            {"event_id": 3, "action": "A → B", "captain": "Palmer"}
        ],
        "chip_targets": [],
    }

    changed = with_plan_changes(plan, previous)

    assert any("transfer plan changed" in item for item in changed.changes)
    assert any("captain changed" in item for item in changed.changes)
