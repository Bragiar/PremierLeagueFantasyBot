from fpl_bot.models import OwnedPlayer
from fpl_bot.recommender import _engine_options


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
