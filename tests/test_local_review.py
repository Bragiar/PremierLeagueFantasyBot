import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

from fpl_bot.cli import build_parser
from fpl_bot.fpl_api import FPLAPIError, FPLClient
from fpl_bot.service import run


def prepare_repository(tmp_path: Path) -> Path:
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
    return tmp_path


def test_preview_writes_output_but_not_state_or_decision_log(tmp_path, monkeypatch):
    repository = prepare_repository(tmp_path)
    original_state = (repository / "state" / "last_run.json").read_text()

    def unavailable(_client):
        raise FPLAPIError("simulated outage")

    monkeypatch.setattr(FPLClient, "bootstrap", unavailable)
    result = run(
        repository,
        preview=True,
        force=True,
        now=datetime(2026, 8, 27, 17, 30, tzinfo=UTC),
        disable_openai=True,
    )

    assert result.status == "preview"
    assert (repository / "outputs" / "latest_recommendation.md").exists()
    assert not (repository / "logs" / "decision_log.jsonl").exists()
    assert (repository / "state" / "last_run.json").read_text() == original_state


def test_cli_accepts_local_review_controls():
    args = build_parser().parse_args(
        [
            "--preview",
            "--force",
            "--no-openai",
            "--select-option",
            "hold",
            "--select-chip",
            "chip:none",
        ]
    )

    assert args.preview is True
    assert args.no_openai is True
    assert args.select_option == "hold"
    assert args.select_chip == "chip:none"


def test_test_telegram_is_labelled_and_does_not_claim_real_window(tmp_path, monkeypatch):
    repository = prepare_repository(tmp_path)
    delivered = []

    def unavailable(_client):
        raise FPLAPIError("simulated outage")

    def capture(_token, _chat_id, message):
        delivered.append(message)

    monkeypatch.setattr(FPLClient, "bootstrap", unavailable)
    monkeypatch.setattr("fpl_bot.service.send_telegram", capture)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "test-chat")

    result = run(
        repository,
        test_telegram=True,
        force=True,
        now=datetime(2026, 8, 27, 17, 30, tzinfo=UTC),
        disable_openai=True,
    )

    assert result.status == "test_sent"
    assert delivered[0].startswith("🧪 TEST ONLY")
    state = json.loads((repository / "state" / "last_run.json").read_text())
    assert state["sent_notifications"] == {}
    record = json.loads((repository / "logs" / "decision_log.jsonl").read_text())
    assert record["delivery"] == "test_sent"


def test_reviewed_option_cannot_be_validated_during_api_failure(tmp_path, monkeypatch):
    repository = prepare_repository(tmp_path)

    def unavailable(_client):
        raise FPLAPIError("simulated outage")

    monkeypatch.setattr(FPLClient, "bootstrap", unavailable)

    try:
        run(
            repository,
            dry_run=True,
            force=True,
            now=datetime(2026, 8, 27, 17, 30, tzinfo=UTC),
            disable_openai=True,
            selected_option_id="hold",
        )
    except ValueError as exc:
        assert "without live FPL data" in str(exc)
    else:
        raise AssertionError("reviewed option should not bypass live validation")
