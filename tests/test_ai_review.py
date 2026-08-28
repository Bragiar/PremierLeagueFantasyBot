import json
from datetime import UTC, datetime
from types import SimpleNamespace

import openai

from fpl_bot.ai import research_recommendation
from fpl_bot.models import (
    ChipOption,
    EngineOption,
    Event,
    Recommendation,
    ResearchReview,
    ResearchSource,
)
from fpl_bot.service import should_apply_research_override


class FakeResponse:
    def __init__(self, payload, sources):
        self.output_text = json.dumps(payload)
        self._sources = sources

    def model_dump(self):
        return {
            "output": [
                {
                    "type": "web_search_call",
                    "action": {"type": "search", "sources": self._sources},
                }
            ]
        }


def recommendation():
    return Recommendation(
        event=Event(2, "Gameweek 2", datetime(2026, 8, 28, 17, 30, tzinfo=UTC)),
        transfers=[],
        points_hit=0,
        captain="Captain",
        vice_captain="Vice",
        starting_xi=[],
        bench=[],
        reserve_goalkeeper="Keeper",
        chip="None",
        confidence="High",
        explanation="Engine prefers holding.",
        selected_option_id="hold",
        engine_options=[
            EngineOption("hold", "Roll", 0.0, "Preserve flexibility"),
            EngineOption("transfer:1:2", "A → B", 4.2, "Higher projection"),
        ],
        selected_chip_id="chip:none",
        chip_options=[
            ChipOption("chip:none", "None", 0.0, "Save it"),
            ChipOption("chip:triple_captain", "Triple Captain", 8.0, "Captain upside"),
        ],
    )


def install_fake_client(monkeypatch, response, captured):
    def create(**kwargs):
        captured.update(kwargs)
        return response

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        openai,
        "OpenAI",
        lambda **_kwargs: SimpleNamespace(responses=SimpleNamespace(create=create)),
    )


def test_research_uses_web_search_and_keeps_only_verified_sources(monkeypatch):
    source_url = "https://example.com/team-news"
    payload = {
        "verdict": "disagree",
        "confidence": "high",
        "recommended_option_id": "transfer:1:2",
        "recommended_chip_id": "chip:none",
        "summary": "Current team news supports the transfer.",
        "risks": ["Possible rotation"],
        "sources": [
            {"title": "Team news", "url": source_url, "date": "2026-08-28"},
            {"title": "Invented", "url": "https://invented.invalid", "date": "today"},
        ],
    }
    captured = {}
    install_fake_client(
        monkeypatch,
        FakeResponse(payload, [{"title": "Team news", "url": source_url}]),
        captured,
    )

    review, error = research_recommendation(recommendation(), {"enabled": True})

    assert error is None
    assert review is not None
    assert review.recommended_option_id == "transfer:1:2"
    assert [source.url for source in review.sources] == [source_url]
    assert captured["tools"] == [{"type": "web_search"}]
    assert captured["tool_choice"] == "required"


def test_research_cannot_invent_an_option(monkeypatch):
    payload = {
        "verdict": "disagree",
        "confidence": "high",
        "recommended_option_id": "transfer:99:100",
        "recommended_chip_id": "chip:none",
        "summary": "Try something else.",
        "risks": [],
        "sources": [],
    }
    install_fake_client(monkeypatch, FakeResponse(payload, []), {})

    review, error = research_recommendation(recommendation(), {"enabled": True})

    assert review is None
    assert "non-shortlisted" in str(error)


def test_research_without_verified_sources_cannot_change_choice(monkeypatch):
    payload = {
        "verdict": "disagree",
        "confidence": "high",
        "recommended_option_id": "transfer:1:2",
        "recommended_chip_id": "chip:none",
        "summary": "An unsupported view.",
        "risks": [],
        "sources": [{"title": "Claim", "url": "https://invented.invalid", "date": "today"}],
    }
    install_fake_client(monkeypatch, FakeResponse(payload, []), {})

    review, error = research_recommendation(recommendation(), {"enabled": True})

    assert error is None
    assert review is not None
    assert review.verdict == "insufficient_evidence"
    assert review.recommended_option_id == "hold"


def test_override_requires_high_confidence_and_two_verified_sources():
    sources = (
        ResearchSource("One", "https://one.example", "today"),
        ResearchSource("Two", "https://two.example", "today"),
    )
    review = ResearchReview(
        verdict="disagree",
        confidence="high",
        recommended_option_id="transfer:1:2",
        summary="Change it",
        risks=(),
        sources=sources,
    )

    assert should_apply_research_override(review, "hold", "chip:none", {})
    assert not should_apply_research_override(
        ResearchReview(**{**review.__dict__, "confidence": "medium"}),
        "hold",
        "chip:none",
        {},
    )
    assert not should_apply_research_override(
        ResearchReview(**{**review.__dict__, "sources": sources[:1]}),
        "hold",
        "chip:none",
        {},
    )
