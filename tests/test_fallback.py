import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

from fpl_bot.fpl_api import FPLAPIError, FPLClient
from fpl_bot.models import Event, SquadEntry, SquadSettings
from fpl_bot.recommender import fallback_recommendation
from fpl_bot.service import run


def test_fallback_is_safe_and_legal_shape():
    entries = (
        *(SquadEntry(name, "GK") for name in ["GK One", "GK Two"]),
        *(SquadEntry(name, "DEF") for name in ["D1", "D2", "D3", "D4", "D5"]),
        *(SquadEntry(name, "MID") for name in ["M1", "M2", "M3", "M4", "M5"]),
        *(SquadEntry(name, "FWD") for name in ["F1", "F2", "F3"]),
    )
    settings = SquadSettings(
        entries=entries,
        bank=0,
        free_transfers=1,
        captain="F1",
        vice_captain="M1",
    )
    event = Event(1, "Gameweek 1", datetime(2026, 8, 21, 17, 30, tzinfo=UTC))

    result = fallback_recommendation(event, settings, "API failure")

    assert result.fallback is True
    assert result.transfers == []
    assert result.points_hit == 0
    assert result.captain == "F1"
    assert result.vice_captain == "M1"
    assert len(result.starting_xi) == 11
    assert len(result.bench) == 3
    assert result.confidence == "Low"
    assert "no transfer" in result.explanation.lower()


def test_service_records_fallback_when_official_api_fails(tmp_path, monkeypatch):
    repository = Path(__file__).resolve().parents[1]
    for directory in ["config", "data", "logs", "outputs", "state"]:
        (tmp_path / directory).mkdir()
    shutil.copy(repository / "config" / "strategy.yaml", tmp_path / "config" / "strategy.yaml")
    shutil.copy(repository / "data" / "squad.yaml", tmp_path / "data" / "squad.yaml")
    (tmp_path / "state" / "last_run.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sent_notifications": {},
                "last_known_events": [
                    {
                        "id": 2,
                        "name": "Gameweek 2",
                        "deadline_time": "2026-08-28T17:30:00Z",
                        "finished": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    def unavailable(_client):
        raise FPLAPIError("simulated outage")

    monkeypatch.setattr(FPLClient, "bootstrap", unavailable)
    result = run(
        tmp_path,
        dry_run=True,
        now=datetime(2026, 8, 27, 17, 30, tzinfo=UTC),
        disable_openai=True,
    )

    assert result.exit_code == 0
    assert result.status == "dry_run"
    assert "Safe fallback" in (tmp_path / "outputs" / "latest_recommendation.md").read_text()
    record = json.loads((tmp_path / "logs" / "decision_log.jsonl").read_text())
    assert record["recommendation"]["fallback"] is True
    assert record["delivery"] == "dry_run"
