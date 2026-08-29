from __future__ import annotations

from datetime import datetime
from typing import Any

from fpl_bot.fpl_api import FPLAPIError, FPLClient
from fpl_bot.models import Recommendation


def empty_forecast_history() -> dict[str, Any]:
    return {"schema_version": 1, "forecasts": {}, "settled": {}}


def normalize_forecast_history(value: dict[str, Any] | None) -> dict[str, Any]:
    history = value if isinstance(value, dict) else empty_forecast_history()
    history.setdefault("schema_version", 1)
    if not isinstance(history.get("forecasts"), dict):
        history["forecasts"] = {}
    if not isinstance(history.get("settled"), dict):
        history["settled"] = {}
    return history


def record_forecast(
    history: dict[str, Any], recommendation: Recommendation, recorded_at: datetime
) -> None:
    history = normalize_forecast_history(history)
    history["forecasts"][str(recommendation.event.id)] = {
        "event_id": recommendation.event.id,
        "event_name": recommendation.event.name,
        "recorded_at": recorded_at.isoformat(),
        "captain": recommendation.captain,
        "vice_captain": recommendation.vice_captain,
        "selected_option_id": recommendation.selected_option_id,
        "selected_chip_id": recommendation.selected_chip_id,
        "points_hit": recommendation.points_hit,
        "risk_mode": recommendation.risk_mode,
        "projections": [
            projection.to_dict() for projection in recommendation.player_projections
        ],
    }


def _settle_one(
    forecast: dict[str, Any], live: dict[str, Any]
) -> dict[str, Any]:
    actual_by_id = {
        int(item["id"]): item.get("stats", {})
        for item in live.get("elements", [])
        if isinstance(item, dict) and item.get("id") is not None
    }
    comparisons: list[dict[str, Any]] = []
    for projection in forecast.get("projections", []):
        if not isinstance(projection, dict):
            continue
        player_id = int(projection.get("player_id", 0) or 0)
        stats = actual_by_id.get(player_id)
        if stats is None:
            continue
        actual_points = float(stats.get("total_points", 0) or 0)
        actual_minutes = float(stats.get("minutes", 0) or 0)
        expected_points = float(projection.get("expected_points", 0) or 0)
        expected_minutes = float(projection.get("expected_minutes", 0) or 0)
        comparisons.append(
            {
                "player_id": player_id,
                "player": str(projection.get("player", player_id)),
                "role": str(projection.get("role", "tracked")),
                "expected_points": round(expected_points, 2),
                "actual_points": round(actual_points, 2),
                "absolute_points_error": round(abs(expected_points - actual_points), 2),
                "expected_minutes": round(expected_minutes, 1),
                "actual_minutes": round(actual_minutes, 1),
                "absolute_minutes_error": round(abs(expected_minutes - actual_minutes), 1),
            }
        )

    count = len(comparisons)
    points_mae = (
        sum(item["absolute_points_error"] for item in comparisons) / count
        if count
        else 0.0
    )
    minutes_mae = (
        sum(item["absolute_minutes_error"] for item in comparisons) / count
        if count
        else 0.0
    )
    starters = [
        item
        for item in comparisons
        if item["role"] in {"starter", "captain", "vice-captain"}
    ]
    expected_team = sum(item["expected_points"] for item in starters)
    actual_team = sum(item["actual_points"] for item in starters)
    captain = next(
        (item for item in comparisons if item["role"] == "captain"), None
    )
    if captain is not None:
        expected_team += captain["expected_points"]
        actual_team += captain["actual_points"]
        if forecast.get("selected_chip_id") == "chip:triple_captain":
            expected_team += captain["expected_points"]
            actual_team += captain["actual_points"]
    if forecast.get("selected_chip_id") == "chip:bench_boost":
        substitutes = [
            item
            for item in comparisons
            if item["role"] in {"bench", "reserve goalkeeper"}
        ]
        expected_team += sum(item["expected_points"] for item in substitutes)
        actual_team += sum(item["actual_points"] for item in substitutes)
    points_hit = max(0, int(forecast.get("points_hit", 0) or 0))
    expected_team -= points_hit
    actual_team -= points_hit

    expected_starts = [item for item in comparisons if item["expected_minutes"] >= 60]
    start_hits = sum(item["actual_minutes"] >= 60 for item in expected_starts)
    return {
        "event_id": int(forecast.get("event_id", 0) or 0),
        "forecast_recorded_at": forecast.get("recorded_at"),
        "selected_option_id": forecast.get("selected_option_id", "hold"),
        "selected_chip_id": forecast.get("selected_chip_id", "chip:none"),
        "points_hit": points_hit,
        "captain": forecast.get("captain", ""),
        "points_mae": round(points_mae, 3),
        "minutes_mae": round(minutes_mae, 3),
        "expected_team_points": round(expected_team, 2),
        "actual_team_points": round(actual_team, 2),
        "expected_starter_hit_rate": (
            round(start_hits / len(expected_starts), 3) if expected_starts else None
        ),
        "players": comparisons,
    }


def settle_finished_forecasts(
    history: dict[str, Any], bootstrap: dict[str, Any], client: FPLClient
) -> list[int]:
    history = normalize_forecast_history(history)
    finished = {
        int(event["id"])
        for event in bootstrap.get("events", [])
        if isinstance(event, dict) and event.get("finished") is True
    }
    settled_ids: list[int] = []
    for raw_id, forecast in list(history["forecasts"].items()):
        try:
            event_id = int(raw_id)
        except (TypeError, ValueError):
            continue
        if event_id not in finished or raw_id in history["settled"]:
            continue
        if not isinstance(forecast, dict):
            continue
        try:
            live = client.event_live(event_id)
        except FPLAPIError:
            continue
        history["settled"][raw_id] = _settle_one(forecast, live)
        settled_ids.append(event_id)
    return settled_ids


def performance_summary(history: dict[str, Any]) -> dict[str, Any] | None:
    settled = [
        item
        for item in history.get("settled", {}).values()
        if isinstance(item, dict)
    ]
    if not settled:
        return None
    recent = sorted(settled, key=lambda item: int(item.get("event_id", 0)))[-6:]
    return {
        "gameweeks": len(recent),
        "points_mae": round(
            sum(float(item.get("points_mae", 0)) for item in recent) / len(recent),
            3,
        ),
        "minutes_mae": round(
            sum(float(item.get("minutes_mae", 0)) for item in recent) / len(recent),
            3,
        ),
    }
