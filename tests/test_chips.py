from datetime import UTC, datetime

from fpl_bot.models import Event, OwnedPlayer, SquadEntry, SquadSettings
from fpl_bot.recommender import _chip_options, _default_chip_id


def settings_for(players, *, status="available"):
    names = ("wildcard", "free_hit", "bench_boost", "triple_captain")
    return SquadSettings(
        entries=tuple(SquadEntry(player.name, player.position, player.cost) for player in players),
        bank=0,
        free_transfers=1,
        captain=players[-1].name,
        vice_captain=players[-2].name,
        chips={
            "first_half": {name: status for name in names},
            "second_half": {name: status for name in names},
        },
    )


def test_chip_options_calculate_triple_captain_and_bench_uplift(legal_players):
    scores = {player.id: 5.0 for player in legal_players}
    captain = legal_players[-1]
    scores[captain.id] = 8.0
    bench = legal_players[8:11]
    reserve_goalkeeper = legal_players[1]
    event = Event(2, "Gameweek 2", datetime(2026, 8, 28, 17, 30, tzinfo=UTC))

    options = _chip_options(
        event,
        [OwnedPlayer(player, player.cost) for player in legal_players],
        legal_players,
        legal_players,
        scores,
        scores,
        captain,
        bench,
        reserve_goalkeeper,
        settings_for(legal_players),
        {},
    )
    by_id = {option.id: option for option in options}

    assert by_id["chip:triple_captain"].projected_uplift == 8.0
    assert by_id["chip:bench_boost"].projected_uplift == 20.0
    assert len(by_id["chip:free_hit"].squad) == 15
    assert len(by_id["chip:wildcard"].squad) == 15


def test_used_chips_are_not_offered(legal_players):
    scores = {player.id: 5.0 for player in legal_players}
    event = Event(2, "Gameweek 2", datetime(2026, 8, 28, 17, 30, tzinfo=UTC))

    options = _chip_options(
        event,
        [OwnedPlayer(player, player.cost) for player in legal_players],
        legal_players,
        legal_players,
        scores,
        scores,
        legal_players[-1],
        legal_players[8:11],
        legal_players[1],
        settings_for(legal_players, status="used"),
        {},
    )

    assert [option.id for option in options] == ["chip:none"]


def test_conservative_policy_saves_non_exceptional_chip():
    from fpl_bot.models import ChipOption

    event = Event(2, "Gameweek 2", datetime(2026, 8, 28, 17, 30, tzinfo=UTC))
    options = [
        ChipOption("chip:none", "None", 0.0, "Save"),
        ChipOption("chip:triple_captain", "Triple Captain", 8.0, "Uplift"),
    ]

    assert _default_chip_id(event, options, {"save_chips_by_default": True}) == "chip:none"
