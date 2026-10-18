from dataclasses import replace
from datetime import UTC, datetime

import pytest

from fpl_bot.models import EngineOption, Event, OwnedPlayer, Recommendation
from fpl_bot.planner import build_rolling_plan
from fpl_bot.recommender import _optimize_squad, _squad_objective
from fpl_bot.squad import selling_price, validate_squad
from fpl_bot.wildcard_review import compare_wildcard_routes, render_wildcard_review
from fpl_bot.render import render_markdown, transfer_lines
from test_chips import settings_for
from test_planner import planner_strategy


def fixtures_for(weeks):
    return [dict(event=week, finished=False, team_h=team, team_a=team + 1,
                 team_h_difficulty=3, team_a_difficulty=3)
            for week in weeks for team in (1, 3, 5)]


def test_wildcard_objective_rotates_lineup_and_captain_each_week(legal_players):
    first = {player.id: 3.0 for player in legal_players}
    second = dict(first)
    first[legal_players[-1].id] = 12.0
    second[legal_players[-2].id] = 12.0
    aggregate = {player.id: first[player.id] + second[player.id] for player in legal_players}
    squad, score = _optimize_squad(
        legal_players, aggregate, 750, bench_weight=.18, weekly_scores=[first, second],
    )
    assert score == pytest.approx(sum(_squad_objective(squad, week, .18)
                                     for week in (first, second)))
    assert score > _squad_objective(squad, aggregate, .18)


def test_required_captain_survives_optimizer_search(legal_players, make_player):
    anchor = legal_players[-1]
    replacement = make_player(101, "FWD", 20)
    scores = {player.id: 3.0 for player in legal_players}
    scores[anchor.id] = 0.0
    scores[replacement.id] = 12.0
    squad, _ = _optimize_squad(
        [*legal_players, replacement], scores, 750, bench_weight=.18,
        required_ids=frozenset({anchor.id}),
    )
    assert anchor in squad
    assert not validate_squad(squad)


def test_retaining_appreciated_players_does_not_charge_a_market_repurchase(legal_players):
    players = [replace(player, cost=52) for player in legal_players]
    retained = {player.id: selling_price(player.cost, 50) for player in players}
    budget = sum(retained.values())
    scores = {player.id: 4.0 for player in players}
    with pytest.raises(ValueError, match="budget|value"):
        _optimize_squad(players, scores, budget, bench_weight=.18)
    squad, _ = _optimize_squad(players, scores, budget, bench_weight=.18,
                               purchase_costs=retained)
    assert len(squad) == 15
    assert sum(retained[player.id] for player in squad) == budget


def test_scheduled_wildcard_is_legal_preserves_fts_and_uses_same_horizon(legal_players):
    event = Event(7, "Gameweek 7", datetime(2026, 10, 17, 10, tzinfo=UTC))
    settings = replace(settings_for(legal_players), free_transfers=2, bank=3)
    plan = build_rolling_plan(
        event, [], [OwnedPlayer(player, player.cost) for player in legal_players],
        legal_players, legal_players, fixtures_for(range(7, 10)), settings,
        planner_strategy(), [], "chip:none", legal_players[-1].name,
        include_chip_targets=False, scheduled_wildcard_event_id=8,
    )
    assert [week.event_id for week in plan.gameweeks] == [7, 8, 9]
    assert [week.chip for week in plan.gameweeks] == ["None", "Wildcard", "None"]
    assert plan.gameweeks[0].free_transfers_after == 3
    assert plan.gameweeks[1].free_transfers_after == 3
    assert all(week.bank_after >= 0 and len(week.starting_xi) == 11 for week in plan.gameweeks)
    assert plan.total_projected_score == round(sum(w.projected_score for w in plan.gameweeks), 2)


def test_scheduled_wildcard_cannot_use_a_spent_chip(legal_players):
    with pytest.raises(ValueError, match="unavailable"):
        build_rolling_plan(
            Event(7, "GW7", datetime(2026, 10, 17, tzinfo=UTC)), [],
            [OwnedPlayer(player, player.cost) for player in legal_players],
            legal_players, legal_players, fixtures_for(range(7, 10)),
            settings_for(legal_players, status="used"), planner_strategy(), [],
            "chip:none", legal_players[-1].name,
            include_chip_targets=False, scheduled_wildcard_event_id=8,
        )


def test_comparison_keeps_selected_decision_and_reports_chip_opportunity_cost(legal_players):
    event = Event(7, "GW7", datetime(2026, 10, 17, tzinfo=UTC))
    recommendation = Recommendation(
        event=event, transfers=[], points_hit=0, captain=legal_players[-1].name,
        vice_captain=legal_players[-2].name, starting_xi=[], bench=[],
        reserve_goalkeeper="", chip="None", confidence="Medium", explanation="",
        engine_options=[EngineOption("hold", "Roll", 0.0, "Save")],
    )
    before = recommendation.to_dict()
    review = compare_wildcard_routes(
        event, [OwnedPlayer(player, player.cost) for player in legal_players],
        legal_players, [], fixtures_for(range(7, 10)), settings_for(legal_players),
        planner_strategy(), recommendation,
    )
    assert not review["failures"]
    assert {route["wildcard_event_id"] for route in review["routes"]} == {None, 7, 8}
    assert all(route["plan"]["horizon"] == 3 for route in review["routes"])
    assert recommendation.to_dict() == before
    assert "not priced" in " ".join(review["limitations"])
    assert "No chip has been activated" in render_wildcard_review(review)
    recommendation.selected_chip_id = "chip:wildcard"
    recommendation.chip = "Wildcard"
    assert transfer_lines(recommendation) == ["Transfers: Wildcard squad rebuild"]
    assert "**Transfers:** Wildcard squad rebuild" in render_markdown(recommendation, "manual")
