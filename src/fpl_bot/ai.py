from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from fpl_bot.models import Recommendation, ResearchReview, ResearchSource


_REVIEW_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "verdict": {
            "type": "string",
            "enum": ["agree", "agree_with_caution", "disagree", "insufficient_evidence"],
        },
        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
        "recommended_option_id": {"type": "string"},
        "recommended_chip_id": {"type": "string"},
        "summary": {"type": "string"},
        "risks": {"type": "array", "items": {"type": "string"}, "maxItems": 5},
        "sources": {
            "type": "array",
            "maxItems": 6,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title": {"type": "string"},
                    "url": {"type": "string"},
                    "date": {"type": "string"},
                },
                "required": ["title", "url", "date"],
            },
        },
    },
    "required": [
        "verdict",
        "confidence",
        "recommended_option_id",
        "recommended_chip_id",
        "summary",
        "risks",
        "sources",
    ],
}


def _normalize_url(value: str) -> str:
    parts = urlsplit(value.strip())
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), parts.query, "")
    )


def _response_web_sources(response: Any) -> dict[str, str]:
    """Collect only URLs returned by web search, not model-authored URLs."""
    dumped = response.model_dump() if hasattr(response, "model_dump") else {}
    found: dict[str, str] = {}

    def visit(value: Any, inside_web_call: bool = False) -> None:
        if isinstance(value, dict):
            is_web_call = inside_web_call or value.get("type") == "web_search_call"
            if is_web_call and isinstance(value.get("url"), str):
                url = str(value["url"])
                found[_normalize_url(url)] = str(value.get("title") or url)
            for child in value.values():
                visit(child, is_web_call)
        elif isinstance(value, list):
            for child in value:
                visit(child, inside_web_call)

    visit(dumped)
    return found


def _review_payload(recommendation: Recommendation) -> dict[str, Any]:
    return {
        "event": {
            "name": recommendation.event.name,
            "deadline": recommendation.event.deadline.isoformat(),
        },
        "engine_selection": recommendation.selected_option_id,
        "engine_explanation": recommendation.explanation,
        "options": [option.to_dict() for option in recommendation.engine_options],
        "engine_chip_selection": recommendation.selected_chip_id,
        "chip_options": [option.to_dict() for option in recommendation.chip_options],
        "captain": recommendation.captain,
        "vice_captain": recommendation.vice_captain,
        "rolling_plan": (
            None
            if recommendation.rolling_plan is None
            else recommendation.rolling_plan.to_dict()
        ),
    }


def research_recommendation(
    recommendation: Recommendation, config: dict[str, Any]
) -> tuple[ResearchReview | None, str | None]:
    """Research and challenge a legal engine shortlist without inventing new moves."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or not bool(config.get("enabled", True)):
        return None, None
    if not bool(config.get("web_research", True)):
        return None, None
    if not recommendation.engine_options:
        return None, "No engine shortlist was available for research"

    try:
        from openai import OpenAI

        model = os.getenv("OPENAI_MODEL", "gpt-5.6-sol").strip() or "gpt-5.6-sol"
        client = OpenAI(api_key=api_key, timeout=45.0, max_retries=1)
        allowed_ids = [option.id for option in recommendation.engine_options]
        allowed_chip_ids = [option.id for option in recommendation.chip_options]
        response = client.responses.create(
            model=model,
            reasoning={"effort": str(config.get("reasoning_effort", "low"))},
            tools=[{"type": "web_search"}],
            tool_choice="required",
            max_tool_calls=int(config.get("max_web_search_calls", 5)),
            include=["web_search_call.action.sources"],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "fpl_research_review",
                    "strict": True,
                    "schema": _REVIEW_SCHEMA,
                }
            },
            instructions=(
                "You are the independent research reviewer for a Fantasy Premier League "
                "recommendation engine. Search the current web before answering. Challenge "
                "the engine using recent official team news, press conferences, reliable "
                "predicted lineups, role or set-piece changes, and respected FPL analysis. "
                "Prefer primary and recent sources. Never invent a transfer: recommended_option_id "
                f"must be exactly one of {allowed_ids!r}. Never invent or assume chip availability: "
                f"recommended_chip_id must be exactly one of {allowed_chip_ids!r}. Compare the "
                "current chip opportunity with likely stronger Blank/Double Gameweeks before its "
                "half-season expiry. Review the rolling route and provisional chip calendar too; "
                "future weeks are conditional projections, not confirmed actions. Free Hit or "
                "Wildcard should be paired with the hold transfer "
                "option because their unlimited transfers supersede a normal transfer. "
                "Distinguish facts from expert opinion. "
                "Use insufficient_evidence when timely evidence is weak. Keep the summary concise."
            ),
            input=json.dumps(_review_payload(recommendation), ensure_ascii=False),
        )
        parsed = json.loads(response.output_text)
        option_id = str(parsed["recommended_option_id"])
        chip_id = str(parsed["recommended_chip_id"])
        if option_id not in allowed_ids:
            return None, f"OpenAI returned non-shortlisted option {option_id!r}"
        if chip_id not in allowed_chip_ids:
            return None, f"OpenAI returned unavailable chip option {chip_id!r}"

        web_sources = _response_web_sources(response)
        sources: list[ResearchSource] = []
        for raw in parsed.get("sources", []):
            normalized = _normalize_url(str(raw.get("url", "")))
            if normalized not in web_sources:
                continue
            sources.append(
                ResearchSource(
                    title=str(raw.get("title") or web_sources[normalized])[:180],
                    url=str(raw["url"]),
                    date=str(raw.get("date") or "not stated")[:40],
                )
            )

        verdict = str(parsed["verdict"])
        confidence = str(parsed["confidence"])
        if not sources:
            verdict = "insufficient_evidence"
            confidence = "low"
            option_id = recommendation.selected_option_id
            chip_id = recommendation.selected_chip_id

        summary_limit = int(config.get("max_explanation_characters", 700))
        return (
            ResearchReview(
                verdict=verdict,
                confidence=confidence,
                recommended_option_id=option_id,
                recommended_chip_id=chip_id,
                summary=str(parsed["summary"])[:summary_limit],
                risks=tuple(str(item)[:240] for item in parsed.get("risks", [])[:5]),
                sources=tuple(sources),
            ),
            None,
        )
    except Exception as exc:  # The deterministic plan must survive every research failure.
        return None, f"{type(exc).__name__}: optional web research unavailable"
