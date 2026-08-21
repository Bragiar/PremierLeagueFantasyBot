from fpl_bot.models import OwnedPlayer, Transfer
from fpl_bot.squad import apply_and_validate_transfers, selling_price


def test_selling_price_uses_half_of_price_rise():
    assert selling_price(current_price=75, purchase_price=65) == 70
    assert selling_price(current_price=60, purchase_price=65) == 60
    assert selling_price(current_price=75, purchase_price=None) == 75


def test_affordable_transfer_uses_sale_plus_bank(legal_players, make_player):
    outgoing = legal_players[2]
    outgoing = make_player(outgoing.id, "DEF", outgoing.team_id, cost=75, name="Outgoing")
    legal_players[2] = outgoing
    owned = [OwnedPlayer(player, 65 if player.id == outgoing.id else player.cost) for player in legal_players]
    incoming = make_player(100, "DEF", 20, cost=72, name="Incoming")
    transfer = Transfer(outgoing, incoming, selling_price=70, buying_price=72)

    proposed, bank, errors = apply_and_validate_transfers(owned, [transfer], bank=2)

    assert errors == []
    assert bank == 0
    assert incoming in proposed


def test_unaffordable_transfer_is_rejected(legal_players, make_player):
    outgoing = make_player(legal_players[2].id, "DEF", legal_players[2].team_id, cost=75)
    legal_players[2] = outgoing
    owned = [OwnedPlayer(player, 65 if player.id == outgoing.id else player.cost) for player in legal_players]
    incoming = make_player(101, "DEF", 20, cost=73, name="Too expensive")
    transfer = Transfer(outgoing, incoming, selling_price=70, buying_price=73)

    _, _, errors = apply_and_validate_transfers(owned, [transfer], bank=2)

    assert any("Cannot afford" in error for error in errors)
