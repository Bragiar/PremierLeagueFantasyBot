from dataclasses import replace

from fpl_bot.recommender import score_player, score_player_for_gameweek


def test_immediate_fixture_can_reverse_long_term_defender_ranking(make_player):
    shaw = replace(
        make_player(1, "DEF", 1, name="Shaw"),
        expected_next=1.7,
        points_per_game=1.0,
        form=1.0,
        selected_by_percent=19.6,
        minutes=90,
        starts=1,
        defensive_contribution_per_90=4.0,
    )
    diop = replace(
        make_player(2, "DEF", 2, name="Diop"),
        expected_next=1.0,
        points_per_game=6.0,
        form=6.0,
        selected_by_percent=17.1,
        minutes=450,
        starts=5,
        defensive_contribution_per_90=5.0,
    )
    strategy = {
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
    }

    assert score_player(diop, [4, 4, 3, 3, 2], strategy) > score_player(
        shaw, [2, 3, 4, 3, 3], strategy
    )
    assert score_player_for_gameweek(shaw, [2], strategy) > score_player_for_gameweek(
        diop, [4], strategy
    )


def test_blank_gameweek_player_gets_zero_lineup_score(make_player):
    player = make_player(1, "MID", 1)

    assert score_player_for_gameweek(player, [], {}) == 0.0
    assert score_player(player, [], {}) == 0.0


def test_one_minute_sample_cannot_explode_defensive_contribution_score(make_player):
    player = replace(
        make_player(1, "MID", 1),
        minutes=1,
        starts=0,
        form=1.0,
        points_per_game=1.0,
        expected_next=1.5,
        defensive_contribution_per_90=270.0,
    )
    strategy = {
        "fixture_weight": 0.45,
        "form_weight": 0.8,
        "ownership_weight": 0.08,
        "secure_starter_weight": 1.6,
        "defensive_contribution_weight": 0.35,
    }

    assert score_player(player, [3, 3, 3, 3, 3], strategy) < 20
