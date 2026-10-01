from dataclasses import replace

import pytest

from fpl_bot.models import OwnedPlayer
from fpl_bot.recommender import (
    _choose_transfer,
    _engine_options,
    _price_timing,
    _transfer_choices,
)


def test_engine_exposes_hold_and_ranked_legal_transfer(legal_players, make_player):
    owned = [OwnedPlayer(player, player.cost) for player in legal_players]
    incoming = make_player(100, "DEF", 20, cost=50, name="Strong Defender")
    candidates = [*legal_players, incoming]
    scores = {player.id: 5.0 for player in legal_players}
    scores[incoming.id] = 12.0
    settings = type(
        "Settings",
        (),
        {"free_transfers": 1, "bank": 0},
    )()
    strategy = {
        "max_recommended_transfers": 1,
        "min_transfer_gain": 2.5,
        "research_candidate_transfers": 3,
    }

    options = _engine_options(owned, candidates, scores, settings, strategy, [])

    assert options[0].id == "hold"
    assert options[1].transfer is not None
    assert options[1].transfer.player_in.name == "Strong Defender"
    assert options[1].projected_gain == 7.0
    assert len(options) <= 4


def test_engine_shortlist_is_hold_only_without_free_transfer(legal_players):
    owned = [OwnedPlayer(player, player.cost) for player in legal_players]
    scores = {player.id: 5.0 for player in legal_players}
    settings = type(
        "Settings",
        (),
        {"free_transfers": 0, "bank": 0},
    )()

    options = _engine_options(
        owned,
        legal_players,
        scores,
        settings,
        {"max_recommended_transfers": 1},
        [],
    )

    assert [option.id for option in options] == ["hold"]


def test_bench_only_upgrade_gets_only_weighted_squad_gain(legal_players, make_player):
    owned = [OwnedPlayer(player, player.cost) for player in legal_players]
    outgoing = legal_players[6]
    incoming = make_player(100, outgoing.position, 20, cost=50, name="Bench Upgrade")
    scores = {player.id: 5.0 for player in legal_players}
    scores[outgoing.id] = 0.0
    scores[incoming.id] = 4.0
    settings = type("Settings", (), {"free_transfers": 1, "bank": 0})()

    choices = _transfer_choices(
        owned,
        [*legal_players, incoming],
        scores,
        settings,
        {"transfer_bench_weight": 0.08},
    )
    choice = next(
        item
        for item in choices
        if item.transfer.player_out.id == outgoing.id
        and item.transfer.player_in.id == incoming.id
    )

    assert choice.gain == pytest.approx(0.32)


def test_market_momentum_adds_a_review_candidate_without_adding_points(
    legal_players, make_player
):
    owned = [OwnedPlayer(player, player.cost) for player in legal_players]
    top = make_player(100, "DEF", 20, cost=50, name="Top Defender")
    market = replace(
        make_player(101, "MID", 21, cost=50, name="Market Midfielder"),
        transfers_in_event=10_000,
        transfers_out_event=100,
    )
    scores = {player.id: 5.0 for player in legal_players}
    scores[top.id] = 12.0
    scores[market.id] = 8.0
    settings = type("Settings", (), {"free_transfers": 1, "bank": 0})()
    strategy = {
        "max_recommended_transfers": 1,
        "min_transfer_gain": 2.5,
        "research_candidate_transfers": 1,
        "research_squad_health_transfers": 0,
        "research_market_momentum_transfers": 1,
    }

    options = _engine_options(
        owned, [*legal_players, top, market], scores, settings, strategy, []
    )

    market_option = next(
        option for option in options if option.transfer and option.transfer.player_in.id == 101
    )
    assert market_option.projected_gain == 3.0
    assert "does not add to the points projection" in market_option.rationale


def test_price_timing_reports_real_buy_and_sell_cliffs(make_player):
    outgoing_player = replace(
        make_player(1, "MID", 1, cost=50, name="Faller"),
        raw={
            "price_change_projections": [
                {"offset": 0, "projected_percent": "-95", "likelihood": -4}
            ]
        },
    )
    incoming = replace(
        make_player(2, "MID", 2, cost=50, name="Riser"),
        raw={
            "price_change_projections": [
                {"offset": 0, "projected_percent": "105", "likelihood": 5}
            ]
        },
    )

    priority, notes = _price_timing(
        OwnedPlayer(outgoing_player, 50),
        incoming,
        {"price_change_warning_threshold": 90},
    )

    assert priority == 2.0
    assert any("selling price" in note for note in notes)
    assert any("buying price" in note for note in notes)


def test_two_free_transfers_can_be_selected_when_second_gain_is_material(
    legal_players, make_player
):
    owned = [OwnedPlayer(player, player.cost) for player in legal_players]
    defender = make_player(100, "DEF", 20, cost=50, name="Defender Upgrade")
    midfielder = make_player(101, "MID", 21, cost=50, name="Midfield Upgrade")
    candidates = [*legal_players, defender, midfielder]
    scores = {player.id: 5.0 for player in legal_players}
    scores[defender.id] = 12.0
    scores[midfielder.id] = 12.0
    settings = type("Settings", (), {"free_transfers": 2, "bank": 0})()
    strategy = {
        "max_recommended_transfers": 2,
        "max_points_hit": 0,
        "avoid_optional_transfers": False,
        "min_transfer_gain": 2.5,
        "additional_free_transfer_min_gain": 4.0,
        "immediate_pair_first_seeds": 12,
        "immediate_pair_second_seeds": 8,
    }

    transfers = _choose_transfer(owned, candidates, scores, settings, strategy)

    assert len(transfers) == 2
    assert {transfer.player_in.id for transfer in transfers} == {100, 101}
