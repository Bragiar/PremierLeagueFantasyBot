"""Subscription-authenticated, read-only Codex review of an engine packet."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any

from fpl_bot.ai import _normalize_url, _REVIEW_SCHEMA
from fpl_bot.models import Recommendation, ResearchReview, ResearchSource


def web_urls(events: str) -> set[str]:
    """Trust only URLs present in actual web-tool events, never final prose."""
    found: set[str] = set()

    def visit(value: Any, web: bool = False) -> None:
        if isinstance(value, dict):
            web = web or value.get("type") in {"web_search", "web_search_call"}
            if web and isinstance(value.get("url"), str):
                found.add(_normalize_url(value["url"]))
            for child in value.values():
                visit(child, web)
        elif isinstance(value, list):
            for child in value:
                visit(child, web)

    for line in events.splitlines():
        try:
            visit(json.loads(line))
        except json.JSONDecodeError:
            continue
    return found


def parse_review(raw: dict[str, Any], events: str, rec: Recommendation) -> ResearchReview:
    option = str(raw["recommended_option_id"])
    chip = str(raw["recommended_chip_id"])
    if option not in {o.id for o in rec.engine_options}:
        raise ValueError("Codex selected an option outside the legal shortlist")
    if chip not in {o.id for o in rec.chip_options}:
        raise ValueError("Codex selected a chip outside the legal shortlist")
    verified = web_urls(events)
    sources = {}
    for source in raw["sources"]:
        url = _normalize_url(source["url"])
        if url in verified:
            sources[url] = ResearchSource(str(source["title"])[:180], source["url"], str(source["date"])[:40])
    verdict, confidence = raw["verdict"], raw["confidence"]
    if verdict not in _REVIEW_SCHEMA["properties"]["verdict"]["enum"]:
        raise ValueError("Invalid review verdict")
    if confidence not in {"low", "medium", "high"}:
        raise ValueError("Invalid review confidence")
    if not sources:
        verdict, confidence = "insufficient_evidence", "low"
        option, chip = rec.selected_option_id, rec.selected_chip_id
    return ResearchReview(
        verdict=verdict, confidence=confidence, recommended_option_id=option,
        recommended_chip_id=chip, summary=str(raw["summary"])[:1200],
        risks=tuple(str(r)[:240] for r in raw["risks"][:5]),
        sources=tuple(sources.values()),
    )


def research_with_codex(rec: Recommendation, config: dict[str, Any], root: Path,
                        forecast: dict[str, Any]) -> tuple[ResearchReview | None, str | None]:
    if not config.get("enabled", False):
        return None, None
    # Codex gets no Telegram, FPL, or API credentials in its environment or packet.
    env = {k: v for k, v in os.environ.items()
           if not any(part in k.upper() for part in ("TOKEN", "SECRET", "PASSWORD", "API_KEY"))
           and not k.startswith(("FPL_", "TELEGRAM_"))}
    try:
        with tempfile.TemporaryDirectory(prefix="fpl-review-") as folder:
            work = Path(folder)
            (work / "packet.json").write_text(json.dumps({
                "recommendation": rec.to_dict(), "forecast_history": forecast,
            }, default=str), encoding="utf-8")
            (work / "schema.json").write_text(json.dumps(_REVIEW_SCHEMA), encoding="utf-8")
            prompt = (
                "Independently challenge the attached FPL engine packet using LIVE web search. "
                "Open and inspect the supporting pages so URLs appear in web-tool events. "
                "Check deadline-relevant official availability and press conferences first, then reliable "
                "predicted lineups, roles, set pieces, rotation, Blank/Double Gameweeks and chip expiry. "
                "Distinguish reported facts from expert opinion. Check expected minutes, confidence notes, "
                "forecast errors, the conditional rolling route, and primary/backup chip windows. "
                "Compare chip uplift against stronger opportunities before expiry. Select ONLY exact immediate "
                "engine_options and chip_options IDs. Keep engine choices unless high-confidence evidence from "
                "at least two recent independent sources supports changing them. Pair Wildcard/Free Hit with hold. "
                "Later moves are conditional, never confirmed. If evidence is inconclusive retain engine choices. "
                "Do not run commands, edit files, send messages or call any API yourself. Only use the packet "
                "and web research tools. Return the required JSON review with dated sources.\n\n"
                + (work / "packet.json").read_text(encoding="utf-8")
            )
            result = subprocess.run([
                str(config.get("binary", "codex")), "-c", 'forced_login_method="chatgpt"',
                "--disable", "shell_tool", "--disable", "unified_exec",
                "--search", "exec", "--sandbox", "read-only",
                "--skip-git-repo-check", "--ephemeral", "--json", "-C", folder,
                "--output-schema", str(work / "schema.json"), "-o", str(work / "review.json"), "-",
            ], input=prompt, env=env, capture_output=True, text=True,
                timeout=int(config.get("timeout_seconds", 600)), check=True)
            raw = json.loads((work / "review.json").read_text())
            review = parse_review(raw, result.stdout, rec)
            out = root / "outputs"
            out.mkdir(exist_ok=True)
            (out / "latest_codex_review.json").write_text(json.dumps(raw, indent=2) + "\n")
            (out / "latest_codex_web_events.jsonl").write_text(result.stdout)
            return review, None
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        return None, f"{type(exc).__name__}: subscription Codex review unavailable; kept engine choices"
