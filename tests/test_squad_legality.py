from dataclasses import replace

from fpl_bot.squad import validate_squad


def test_legal_squad_passes_all_rules(legal_players):
    assert validate_squad(legal_players) == []


def test_more_than_three_from_one_club_is_rejected(legal_players):
    illegal = list(legal_players)
    illegal[0] = replace(illegal[0], team_id=99, team_name="Overloaded FC")
    illegal[1] = replace(illegal[1], team_id=99, team_name="Overloaded FC")
    illegal[2] = replace(illegal[2], team_id=99, team_name="Overloaded FC")
    illegal[3] = replace(illegal[3], team_id=99, team_name="Overloaded FC")

    assert any("maximum is 3" in error for error in validate_squad(illegal))


def test_wrong_position_quota_is_rejected(legal_players):
    illegal = list(legal_players)
    illegal[-1] = replace(illegal[-1], position="MID")
    errors = validate_squad(illegal)

    assert any("MID" in error for error in errors)
    assert any("FWD" in error for error in errors)
