"""Non-recording Wildcard counterfactuals on a common, weekly scoring basis."""
from __future__ import annotations

from typing import Any

from fpl_bot.models import Event, OwnedPlayer, Player, Recommendation, SquadSettings
from fpl_bot.planner import _scores_for_event, build_rolling_plan
from fpl_bot.recommender import _captains, _choose_lineup, _optimize_squad
from fpl_bot.squad import apply_and_validate_transfers, selling_price


def compare_wildcard_routes(
    event: Event, owned: list[OwnedPlayer], candidates: list[Player],
    raw_events: list[dict[str, Any]], fixtures: list[dict[str, Any]],
    settings: SquadSettings, strategy: dict[str, Any], recommendation: Recommendation,
) -> dict[str, Any]:
    """Compare bounded routes; never activate a chip or change the selected action.

    All routes use the same dates, prices, projections and ordinary transfer rules.
    The no-chip route retains the Wildcard, whose later option value is unpriced.
    """
    horizon = min(int(strategy.get("fixture_horizon", 5)),
                  int(strategy.get("max_fixture_horizon", 6)), 39 - event.id)
    score_strategy = {**strategy, "completed_gameweeks": max(0, event.id - 1)}
    weekly = [_scores_for_event(candidates, fixtures, week, score_strategy,
                               current_event_id=event.id)
              for week in range(event.id, event.id + horizon)]
    aggregate = {player.id: sum(week[player.id] for week in weekly) for player in candidates}
    half = "first_half" if event.id <= 19 else "second_half"
    if settings.chips.get(half, {}).get("wildcard") != "available":
        return {"event_id": event.id, "horizon": horizon, "routes": [],
                "limitations": ["Wildcard is unavailable in the current half-season."]}
    selected = next(option for option in recommendation.engine_options
                    if option.id == recommendation.selected_option_id)
    hold = next(option for option in recommendation.engine_options if option.id == "hold")
    immediate_options = list({option.id: option for option in (selected, hold)}.values())
    anchor = next((player for player in candidates if player.name == recommendation.captain), None)
    anchors = [("unrestricted", frozenset())]
    if anchor is not None:
        anchors.append((f"keep {anchor.name} at rebuild", frozenset({anchor.id})))
    routes: list[dict[str, Any]] = []
    failures: list[str] = []

    def append_route(label: str, option_id: str, chip_week: int | None,
                     players: list[Player], transfers: list, required: frozenset[int],
                     draft: list[Player] | None = None) -> None:
        lineup, _, _ = _choose_lineup(players, weekly[0])
        captain, _ = _captains(lineup, weekly[0], score_strategy)
        plan = build_rolling_plan(
            event, raw_events, owned, players, candidates, fixtures, settings,
            score_strategy, transfers,
            "chip:wildcard" if chip_week == event.id else "chip:none", captain.name,
            include_chip_targets=False,
            scheduled_wildcard_event_id=chip_week if chip_week != event.id else None,
            wildcard_required_ids=required,
        )
        routes.append({
            "label": label, "immediate_option_id": option_id,
            "wildcard_event_id": chip_week, "score": plan.total_projected_score,
            "wildcard_retained": chip_week is None,
            "wildcard_draft": [player.name for player in (draft or [])],
            "plan": plan.to_dict(),
        })

    for option in immediate_options:
        players, _, errors = apply_and_validate_transfers(owned, list(option.transfers), settings.bank)
        if errors:
            failures.append(f"{option.id}: {'; '.join(errors)}")
            continue
        append_route(f"{option.action}; ordinary transfers", option.id, None,
                     players, list(option.transfers), frozenset())
        if horizon > 1 and event.id != 19:
            for anchor_label, required in anchors:
                try:
                    append_route(f"{option.action}; WC GW{event.id + 1}; {anchor_label}",
                                 option.id, event.id + 1, players, list(option.transfers), required)
                except ValueError as exc:
                    failures.append(f"WC next week ({anchor_label}): {exc}")

    purchase_costs = {item.player.id: selling_price(item.player.cost, item.purchase_price)
                      for item in owned}
    team_value = settings.bank + sum(purchase_costs.values())
    for anchor_label, required in anchors:
        try:
            draft, _ = _optimize_squad(
                candidates, aggregate, team_value, bench_weight=float(strategy.get("planner_bench_weight", .18)),
                strategy=score_strategy, weekly_scores=weekly, required_ids=required,
                initial_squad=[item.player for item in owned], purchase_costs=purchase_costs,
            )
            # build_rolling_plan charges retained players at their opportunity cost.
            append_route(f"WC GW{event.id}; {anchor_label}", "hold", event.id,
                         draft, [], required, draft)
        except ValueError as exc:
            failures.append(f"WC now ({anchor_label}): {exc}")
    baseline = next((route["score"] for route in routes
                     if route["immediate_option_id"] == selected.id
                     and route["wildcard_event_id"] is None), None)
    for route in routes:
        route["delta_vs_selected_no_chip"] = (
            None if baseline is None else round(route["score"] - baseline, 2)
        )
    return {
        "event_id": event.id, "horizon": horizon,
        "baseline_option_id": selected.id,
        "routes": sorted(routes, key=lambda route: route["score"], reverse=True),
        "failures": failures,
        "limitations": [
            "Comparative model scores, not literal point forecasts or guaranteed upside.",
            "Bounded local and beam searches; global optimality is not established.",
            "Prices and current availability/roles are held fixed; recovery and rotation are uncertain.",
            "The no-chip routes retain a Wildcard; its value beyond this horizon is not priced.",
            "Only the selected immediate action and hold are tested before a future Wildcard.",
            "Keeping the captain constrains the rebuild only; later ordinary moves may sell him.",
            "Experimental drafts are comparisons, not newly selected immediate shortlist actions.",
        ],
    }


def render_wildcard_review(review: dict[str, Any]) -> str:
    lines = [f"# Wildcard route comparison — GW{review['event_id']}", "",
             f"Common horizon: {review['horizon']} Gameweeks. No chip has been activated.", "",
             "| Route | Model score | Change vs selected no-chip route | Wildcard retained |",
             "|---|---:|---:|---|"]
    for route in review["routes"]:
        delta = route["delta_vs_selected_no_chip"]
        delta_text = "—" if delta is None else f"{delta:+.2f}"
        lines.append(f"| {route['label']} | {route['score']:.2f} | "
                     f"{delta_text} | {'Yes' if route['wildcard_retained'] else 'No'} |")
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in review["limitations"])
    if review.get("failures"):
        lines.extend(["", "## Infeasible comparisons", ""])
        lines.extend(f"- {item}" for item in review["failures"])
    for route in review["routes"]:
        lines.extend(["", f"## {route['label']}", ""])
        for week in route["plan"]["gameweeks"]:
            action = "Wildcard rebuild" if week["chip"] == "Wildcard" else week["action"]
            lines.append(f"- GW{week['event_id']}: {action}; captain {week['captain']}; "
                         f"bank £{week['bank_after']:.1f}m; next-week FTs {week['free_transfers_after']}.")
            if week["chip"] == "Wildcard":
                lines.append("  - XI: " + ", ".join(week["starting_xi"]) + ".")
                lines.append("  - Bench: " + ", ".join(week["bench"]) + "; GK "
                             + week["reserve_goalkeeper"] + ".")
    return "\n".join(lines) + "\n"
