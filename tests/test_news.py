from dataclasses import replace

from fpl_bot.recommender import availability, news_availability


def test_explicit_official_news_probability_is_used(make_player):
    player = replace(
        make_player(1, "FWD", 1),
        news="Knock - 75% chance of playing",
    )

    assert news_availability(player) == 75
    assert availability(player) == 75


def test_clear_official_unavailability_news_scores_zero(make_player):
    player = replace(
        make_player(1, "FWD", 1),
        news="Injury - Unknown return date",
    )

    assert news_availability(player) == 0
    assert availability(player) == 0


def test_unquantified_injury_news_is_conservative(make_player):
    player = replace(
        make_player(1, "FWD", 1),
        news="Illness - being assessed",
    )

    assert news_availability(player) == 50
    assert availability(player) == 50


def test_news_cannot_override_stronger_api_chance(make_player):
    player = replace(
        make_player(1, "FWD", 1),
        chance_next=25,
        news="Knock - 75% chance of playing",
    )

    assert availability(player) == 25


def test_non_risk_news_does_not_change_availability(make_player):
    player = replace(
        make_player(1, "FWD", 1),
        news="Returned to training",
    )

    assert news_availability(player) is None
    assert availability(player) == 100
