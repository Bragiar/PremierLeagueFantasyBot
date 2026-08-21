from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fpl_bot.ai import add_optional_ai_commentary
from fpl_bot.config import load_squad, load_strategy
from fpl_bot.deadlines import (
    due_window,
    notification_key,
    select_next_event,
    serialize_future_events,
)
from fpl_bot.fpl_api import FPLAPIError, FPLClient
from fpl_bot.models import Event, Recommendation
from fpl_bot.recommender import fallback_recommendation, recommend
from fpl_bot.render import render_markdown, render_telegram
from fpl_bot.squad import resolve_squad
from fpl_bot.storage import append_jsonl, atomic_write_text, load_state, save_state
from fpl_bot.telegram import TelegramError, send_telegram


@dataclass(frozen=True)
class ServiceResult:
    exit_code: int
    status: str
    message: str


def already_notified(state: dict[str, Any], key: str) -> bool:
    sent = state.get("sent_notifications", {})
    return isinstance(sent, dict) and key in sent


def _trim_sent_notifications(state: dict[str, Any], current_event: int) -> None:
    sent = state.get("sent_notifications", {})
    if not isinstance(sent, dict):
        state["sent_notifications"] = {}
        return
    state["sent_notifications"] = {
        key: value
        for key, value in sent.items()
        if (match := re.match(r"gw(\d+):", key)) is None
        or int(match.group(1)) >= current_event - 2
    }


def _record(
    recommendation: Recommendation,
    now: datetime,
    window: str,
    key: str,
    delivery: str,
    ai_used: bool,
    ai_error: str | None,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "recorded_at": now.isoformat(),
        "notification_key": key,
        "window": window,
        "delivery": delivery,
        "ai_used": ai_used,
        "ai_error": ai_error,
        "recommendation": recommendation.to_dict(),
    }


def _fallback_event(state: dict[str, Any], now: datetime) -> Event | None:
    raw_events = state.get("last_known_events", [])
    if not isinstance(raw_events, list):
        return None
    return select_next_event(raw_events, now)


def run(
    repo_root: Path,
    *,
    dry_run: bool = False,
    force: bool = False,
    now: datetime | None = None,
    disable_openai: bool = False,
) -> ServiceResult:
    now = (now or datetime.now(UTC)).astimezone(UTC)
    strategy_config = load_strategy(repo_root / "config" / "strategy.yaml")
    squad_settings = load_squad(repo_root / "data" / "squad.yaml")
    state_path = repo_root / "state" / "last_run.json"
    state = load_state(state_path)

    api_config = strategy_config["fpl_api"]
    client = FPLClient(
        base_url=str(api_config["base_url"]),
        timeout_seconds=int(api_config.get("timeout_seconds", 20)),
        retries=int(api_config.get("retries", 3)),
    )

    bootstrap: dict[str, Any] | None = None
    api_problem: str | None = None
    try:
        bootstrap = client.bootstrap()
        event = select_next_event(bootstrap["events"], now)
    except FPLAPIError as exc:
        api_problem = str(exc)
        event = _fallback_event(state, now)

    if event is None:
        if not force:
            return ServiceResult(0, "no_future_event", "No future FPL deadline is available.")
        event = Event(id=0, name="Unknown Gameweek", deadline=now)

    notifications = strategy_config["notifications"]
    window = due_window(
        event.deadline,
        now,
        notifications["offsets_minutes"],
        int(notifications.get("tolerance_minutes", 40)),
    )
    if not force and window is None:
        remaining = max(0, int((event.deadline - now).total_seconds() // 60))
        return ServiceResult(
            0,
            "not_due",
            f"No deadline action is due; {event.name} is in {remaining} minutes.",
        )
    window = window or "manual"
    key = notification_key(event.id, window)
    if not force and already_notified(state, key):
        return ServiceResult(
            0, "duplicate", f"Notification {key} was already delivered; nothing to do."
        )

    recommendation: Recommendation
    if bootstrap is None:
        recommendation = fallback_recommendation(
            event, squad_settings, api_problem or "official FPL API unavailable"
        )
    else:
        try:
            owned = resolve_squad(
                squad_settings, bootstrap["elements"], bootstrap["teams"]
            )
            fixtures = client.fixtures()
            recommendation = recommend(
                event,
                owned,
                bootstrap,
                fixtures,
                squad_settings,
                strategy_config["strategy"],
            )
        except (FPLAPIError, KeyError, TypeError, ValueError) as exc:
            recommendation = fallback_recommendation(
                event, squad_settings, f"{type(exc).__name__}: live analysis incomplete"
            )

    openai_config = dict(strategy_config["openai"])
    if disable_openai:
        openai_config["enabled"] = False
    ai_used, ai_error = add_optional_ai_commentary(recommendation, openai_config)

    telegram_message = render_telegram(recommendation, window)
    markdown = render_markdown(recommendation, window)
    atomic_write_text(repo_root / "outputs" / "latest_recommendation.md", markdown)

    delivery = "dry_run" if dry_run else "pending"
    delivery_error: str | None = None
    if not dry_run:
        try:
            send_telegram(
                os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
                os.getenv("TELEGRAM_CHAT_ID", "").strip(),
                telegram_message,
            )
            delivery = "sent"
            state.setdefault("sent_notifications", {})[key] = now.isoformat()
        except TelegramError as exc:
            delivery = "failed"
            delivery_error = str(exc)

    if bootstrap is not None:
        state["last_known_events"] = serialize_future_events(
            bootstrap["events"], now
        )
    state["last_run"] = {
        "at": now.isoformat(),
        "event_id": event.id,
        "notification_key": key,
        "window": window,
        "delivery": delivery,
        "fallback": recommendation.fallback,
    }
    _trim_sent_notifications(state, event.id)
    save_state(state_path, state)
    append_jsonl(
        repo_root / "logs" / "decision_log.jsonl",
        _record(recommendation, now, window, key, delivery, ai_used, ai_error),
    )

    if delivery_error:
        return ServiceResult(
            2,
            "delivery_failed",
            f"Recommendation recorded, but {delivery_error.lower()}.",
        )
    return ServiceResult(0, delivery, telegram_message)
