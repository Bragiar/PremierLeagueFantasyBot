from dataclasses import replace

from fpl_bot.models import OwnedPlayer
from fpl_bot.recommender import (
    _captains,
    _choose_transfer,
    _optimizer_pool,
    expected_minutes,
    score_player_for_gameweek,
)
from fpl_bot.squad import inferred_initial_purchase_price


def test_one_match_haul_does_not_overrule_stronger_official_projection(make_player):
    steady = replace(
        make_player(1, "MID", 1, name="Steady"),
        expected_next=5.0,
        form=2.0,
        points_per_game=2.0,
        minutes=90,
        starts=1,
    )
    hauler = replace(
        make_player(2, "MID", 2, name="One-match hauler"),
        expected_next=2.4,
        form=11.0,
        points_per_game=11.0,
        minutes=90,
        starts=1,
    )
    strategy = {
        "completed_gameweeks": 1,
        "lineup_fixture_weight": 1.0,
        "lineup_form_weight": 0.2,
        "lineup_secure_starter_weight": 1.6,
        "lineup_underlying_stats_weight": 0.8,
        "lineup_defensive_contribution_weight": 0.2,
    }

    assert score_player_for_gameweek(steady, [3], strategy) > score_player_for_gameweek(
        hauler, [3], strategy
    )


def test_captaincy_is_not_anchored_to_the_previous_captain(legal_players):
    preferred = legal_players[-3]
    previous = legal_players[-2]
    scores = {player.id: 3.0 for player in legal_players}
    scores[preferred.id] = 7.0
    scores[previous.id] = 5.0
    captain, vice = _captains(
        legal_players,
        scores,
        {"completed_gameweeks": 10, "captain_min_expected_minutes": 60},
    )

    assert captain.id == preferred.id
    assert vice.id == previous.id


def test_zero_minute_player_is_not_an_optimizer_bargain(make_player):
    inactive = replace(
        make_player(1, "FWD", 1, cost=45),
        minutes=0,
        starts=0,
        expected_next=4.0,
    )
    strategy = {"completed_gameweeks": 1, "optimizer_min_expected_minutes": 25}

    assert expected_minutes(inactive, strategy) <= 20
    assert score_player_for_gameweek(inactive, [3], strategy) < 2.0
    assert inactive not in _optimizer_pool([inactive], {inactive.id: 10.0}, strategy)["FWD"]


def test_optional_transfer_waits_for_a_minimum_sample(legal_players, make_player):
    owned = [OwnedPlayer(player, player.cost) for player in legal_players]
    incoming = make_player(100, "DEF", 20, cost=50, name="Incoming")
    scores = {player.id: 5.0 for player in legal_players}
    scores[legal_players[2].id] = 1.0
    scores[incoming.id] = 10.0
    settings = type("Settings", (), {"free_transfers": 1, "bank": 0})()
    base_strategy = {
        "max_recommended_transfers": 1,
        "max_points_hit": 0,
        "avoid_optional_transfers": True,
        "min_transfer_gain": 2.5,
        "optional_transfer_min_completed_gameweeks": 2,
        "optional_transfer_exception_gain": 7.0,
    }

    assert _choose_transfer(
        owned,
        [*legal_players, incoming],
        scores,
        settings,
        {**base_strategy, "completed_gameweeks": 1},
    ) == []
    assert _choose_transfer(
        owned,
        [*legal_players, incoming],
        scores,
        settings,
        {**base_strategy, "completed_gameweeks": 2},
    )[0].player_in.id == incoming.id


def test_opening_purchase_price_is_recovered_from_official_price_change(make_player):
    player = replace(
        make_player(1, "FWD", 1, cost=76),
        raw={"cost_change_start": 1},
    )

    assert inferred_initial_purchase_price(player) == 75
