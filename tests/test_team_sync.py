from __future__ import annotations

from datetime import UTC, datetime

import yaml

from fpl_bot.team_sync import build_synced_settings, render_squad_yaml


def _bootstrap():
    positions = [1, 1] + [2] * 5 + [3] * 5 + [4] * 3
    return {
        "events": [{"id": 3, "is_next": True}],
        "elements": [
            {
                "id": index,
                "web_name": f"Player {index}",
                "element_type": position,
                "team": ((index - 1) % 6) + 1,
            }
            for index, position in enumerate(positions, start=1)
        ],
    }


def _my_team():
    return {
        "picks": [
            {
                "element": index,
                "purchase_price": 40 + index,
                "is_captain": index == 13,
                "is_vice_captain": index == 14,
            }
            for index in range(1, 16)
        ],
        "transfers": {"bank": 5, "limit": 3, "made": 1},
        "chips": [
            {"name": "wildcard", "status": "available"},
            {"name": "freehit", "status": "used"},
        ],
    }


def test_authenticated_team_builds_exact_squad_state():
    previous = {
        "chips": {
            "first_half": {
                "wildcard": "available",
                "free_hit": "available",
                "bench_boost": "available",
                "triple_captain": "available",
            },
            "second_half": {
                "wildcard": "available",
                "free_hit": "available",
                "bench_boost": "available",
                "triple_captain": "available",
            },
        }
    }
    confirmed = datetime(2026, 8, 30, 12, tzinfo=UTC)

    synced = build_synced_settings(
        previous,
        _my_team(),
        _bootstrap(),
        entry_id=12345,
        confirmed_at=confirmed,
    )

    assert synced["bank"] == 0.5
    assert synced["free_transfers"] == 2
    assert synced["captain"] == "Player 13"
    assert synced["vice_captain"] == "Player 14"
    assert synced["squad"][0]["purchase_price"] == 4.1
    assert synced["chips"]["first_half"]["free_hit"] == "used"


def test_rendered_squad_yaml_round_trips():
    synced = build_synced_settings(
        {"chips": {}},
        _my_team(),
        _bootstrap(),
        entry_id=12345,
        confirmed_at=datetime(2026, 8, 30, 12, tzinfo=UTC),
    )

    rendered = render_squad_yaml(synced)
    loaded = yaml.safe_load(rendered)

    assert loaded == synced
    assert "FPL credentials" in rendered
