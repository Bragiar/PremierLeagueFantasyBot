import json
from types import SimpleNamespace
import subprocess

import pytest

from fpl_bot.codex_review import parse_review, research_with_codex, web_urls
from test_ai_review import recommendation


def payload():
    return {"verdict": "disagree", "confidence": "high", "recommended_option_id": "transfer:1:2",
            "recommended_chip_id": "chip:none", "summary": "Recent official news", "risks": [],
            "sources": [{"title": "News", "url": "https://club.example/news", "date": "2026-10-18"}]}


def test_only_actual_web_events_can_verify_a_source():
    prose = json.dumps({"item": {"type": "agent_message", "url": "https://club.example/news"}})
    assert not web_urls(prose)
    review = parse_review(payload(), prose, recommendation())
    assert review.verdict == "insufficient_evidence"
    assert review.recommended_option_id == "hold"
    actual = json.dumps({"item": {"type": "web_search", "action": {
        "type": "open_page", "url": "https://club.example/news"}}})
    assert len(parse_review(payload(), actual, recommendation()).sources) == 1


def test_codex_cannot_select_outside_the_shortlists():
    raw = payload()
    raw["recommended_option_id"] = "transfer:999:111"
    with pytest.raises(ValueError, match="shortlist"):
        parse_review(raw, "", recommendation())


def test_timeout_falls_back_and_does_not_pass_secrets_to_codex(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "do-not-pass")
    monkeypatch.setenv("CODEX_API_KEY", "do-not-pass")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "do-not-pass")
    def timeout(command, **kwargs):
        assert "OPENAI_API_KEY" not in kwargs["env"]
        assert "CODEX_API_KEY" not in kwargs["env"]
        assert "TELEGRAM_BOT_TOKEN" not in kwargs["env"]
        assert command[command.index("--sandbox") + 1] == "read-only"
        raise subprocess.TimeoutExpired(command, 600)
    monkeypatch.setattr(subprocess, "run", timeout)
    review, error = research_with_codex(recommendation(), {"enabled": True}, tmp_path, {})
    assert review is None
    assert "kept engine choices" in error
