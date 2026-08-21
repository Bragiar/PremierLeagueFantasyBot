from __future__ import annotations

from typing import Any

import pytest

from fpl_bot.models import Player


@pytest.fixture
def make_player():
    def factory(
        player_id: int,
        position: str,
        team_id: int,
        *,
        cost: int = 50,
        name: str | None = None,
        status: str = "a",
    ) -> Player:
        player_name = name or f"Player {player_id}"
        raw: dict[str, Any] = {}
        return Player(
            id=player_id,
            name=player_name,
            full_name=player_name,
            position=position,
            team_id=team_id,
            team_name=f"Team {team_id}",
            cost=cost,
            status=status,
            chance_next=None,
            news="",
            can_select=True,
            minutes=900,
            starts=10,
            total_points=50,
            form=4.0,
            points_per_game=4.0,
            selected_by_percent=10.0,
            expected_next=4.0,
            defensive_contribution_per_90=1.0,
            raw=raw,
        )

    return factory


@pytest.fixture
def legal_players(make_player):
    positions = ["GK"] * 2 + ["DEF"] * 5 + ["MID"] * 5 + ["FWD"] * 3
    return [
        make_player(index, position, ((index - 1) % 6) + 1)
        for index, position in enumerate(positions, start=1)
    ]
