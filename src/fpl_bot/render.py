from __future__ import annotations

from fpl_bot.models import Recommendation


def transfer_lines(recommendation: Recommendation) -> list[str]:
    if not recommendation.transfers:
        return ["Transfers: Roll / no transfer"]
    lines = ["Transfers:"]
    for transfer in recommendation.transfers:
        lines.append(
            f"- {transfer.player_out.name} ➜ {transfer.player_in.name} "
            f"(£{transfer.selling_price / 10:.1f}m ➜ £{transfer.buying_price / 10:.1f}m)"
        )
    return lines


def render_telegram(
    recommendation: Recommendation, window: str, *, test_message: bool = False
) -> str:
    deadline = recommendation.event.deadline.strftime("%a %d %b, %H:%M UTC")
    hit = "0" if recommendation.points_hit == 0 else f"-{recommendation.points_hit}"
    lines = [
        *(["🧪 TEST ONLY — NO FPL CHANGES WERE MADE", ""] if test_message else []),
        f"⚽ FPL {recommendation.event.name} plan ({window})",
        f"Deadline: {deadline}",
        "",
        *transfer_lines(recommendation),
        f"Cost / points hit: {hit}",
        f"Captain: {recommendation.captain}",
        f"Vice-captain: {recommendation.vice_captain}",
        "",
        "Starting XI:",
        ", ".join(recommendation.starting_xi),
        "",
        "Bench order:",
        ", ".join(
            f"{index}. {name}" for index, name in enumerate(recommendation.bench, start=1)
        ),
        f"Reserve goalkeeper: {recommendation.reserve_goalkeeper}",
        f"Chip: {recommendation.chip}",
        f"Confidence: {recommendation.confidence}",
        "",
        recommendation.explanation,
    ]
    if recommendation.rolling_plan:
        plan = recommendation.rolling_plan
        lines.extend(["", "Rolling outlook:"])
        for week in plan.gameweeks[1:4]:
            lines.append(
                f"- GW{week.event_id}: {week.action}; captain {week.captain} "
                f"({week.confidence.lower()} confidence)"
            )
        if plan.chip_targets:
            lines.append("Provisional chips:")
            lines.extend(
                f"- {target.chip}: GW{target.primary_event_id}"
                + (f" on {target.target_player}" if target.target_player else "")
                + f" ({target.confidence.lower()})"
                for target in plan.chip_targets
            )
    if recommendation.research_review:
        review = recommendation.research_review
        lines.extend(
            [
                "",
                f"Web research review: {review.verdict.replace('_', ' ').title()} "
                f"({review.confidence})",
                review.summary,
            ]
        )
        if review.risks:
            lines.append("Risks: " + "; ".join(review.risks[:3]))
        if review.sources:
            lines.append("Sources:")
            lines.extend(f"- {source.title}: {source.url}" for source in review.sources[:3])
    message = "\n".join(lines)
    return message[:4096]


def render_markdown(recommendation: Recommendation, window: str) -> str:
    transfer_text = (
        "Roll / no transfer"
        if not recommendation.transfers
        else "<br>".join(
            f"{transfer.player_out.name} → {transfer.player_in.name} "
            f"(£{transfer.selling_price / 10:.1f}m → £{transfer.buying_price / 10:.1f}m)"
            for transfer in recommendation.transfers
        )
    )
    hit = "0" if recommendation.points_hit == 0 else f"-{recommendation.points_hit}"
    lines = [
        f"# {recommendation.event.name} recommendation",
        "",
        f"- **Deadline:** {recommendation.event.deadline.strftime('%Y-%m-%d %H:%M UTC')}",
        f"- **Run window:** {window}",
        f"- **Transfers:** {transfer_text}",
        f"- **Cost / points hit:** {hit}",
        f"- **Captain:** {recommendation.captain}",
        f"- **Vice-captain:** {recommendation.vice_captain}",
        f"- **Chip:** {recommendation.chip}",
        f"- **Confidence:** {recommendation.confidence}",
        f"- **Analysis source:** {recommendation.source}",
        "",
        "## Starting XI",
        "",
        ", ".join(recommendation.starting_xi),
        "",
        "## Bench",
        "",
        ", ".join(
            f"{index}. {name}" for index, name in enumerate(recommendation.bench, start=1)
        ),
        "",
        f"Reserve goalkeeper: {recommendation.reserve_goalkeeper}",
        "",
        "## Explanation",
        "",
        recommendation.explanation,
    ]
    if recommendation.engine_options:
        lines.extend(["", "## Engine shortlist", ""])
        for option in recommendation.engine_options:
            selected = " — selected" if option.id == recommendation.selected_option_id else ""
            lines.append(
                f"- **{option.action}** (`{option.id}`){selected}: projected gain "
                f"{option.projected_gain:+.1f}. {option.rationale}"
            )
    if recommendation.chip_options:
        lines.extend(["", "## Chip shortlist", ""])
        for option in recommendation.chip_options:
            selected = " — selected" if option.id == recommendation.selected_chip_id else ""
            lines.append(
                f"- **{option.chip}** (`{option.id}`){selected}: projected uplift "
                f"{option.projected_uplift:+.1f}. {option.rationale}"
            )
            if option.squad:
                lines.append(
                    "  - Optimized squad: "
                    + ", ".join(player.name for player in option.squad)
                )
    if recommendation.research_review:
        review = recommendation.research_review
        lines.extend(
            [
                "",
                "## Web research review",
                "",
                f"- **Verdict:** {review.verdict.replace('_', ' ').title()}",
                f"- **Confidence:** {review.confidence.title()}",
                f"- **Preferred option:** `{review.recommended_option_id}`",
                f"- **Preferred chip:** `{review.recommended_chip_id}`",
                f"- **Changed engine choice:** {'Yes' if review.changed_engine_choice else 'No'}",
                f"- **Changed chip choice:** {'Yes' if review.changed_chip_choice else 'No'}",
                "",
                review.summary,
            ]
        )
        if review.risks:
            lines.extend(["", "### Risks", ""])
            lines.extend(f"- {risk}" for risk in review.risks)
        if review.sources:
            lines.extend(["", "### Sources checked", ""])
            lines.extend(
                f"- [{source.title}]({source.url}) — {source.date}"
                for source in review.sources
            )
    if recommendation.rolling_plan:
        plan = recommendation.rolling_plan
        lines.extend(
            [
                "",
                "## Rolling short-term plan",
                "",
                f"Combined model score over the {plan.horizon}-Gameweek route: "
                f"**{plan.total_projected_score:.1f}**. This is a comparative rating, "
                "not a literal points forecast.",
                "",
                "| GW | Transfers | Captain | Chip | Hit | Free transfers after | Bank | Model score | Confidence |",
                "|---:|---|---|---|---:|---:|---:|---:|---|",
            ]
        )
        for week in plan.gameweeks:
            week_hit = "0" if week.points_hit == 0 else f"-{week.points_hit}"
            lines.append(
                f"| {week.event_id} | {week.action} | {week.captain} | {week.chip} | "
                f"{week_hit} | {week.free_transfers_after} | "
                f"£{week.bank_after:.1f}m | {week.projected_score:.1f} | "
                f"{week.confidence} |"
            )
        for week in plan.gameweeks:
            lines.extend(
                [
                    "",
                    f"### {week.event_name} projected team",
                    "",
                    f"- **Starting XI:** {', '.join(week.starting_xi)}",
                    f"- **Bench:** {', '.join(week.bench)}; reserve goalkeeper "
                    f"{week.reserve_goalkeeper}",
                    f"- **Reasoning:** {week.rationale}",
                ]
            )
        if plan.chip_targets:
            lines.extend(
                [
                    "",
                    "## Provisional long-term chip calendar",
                    "",
                    "These are decision gates, not chips already applied to the short-term "
                    "route. If one is activated, the route will be rebuilt from the resulting "
                    "squad.",
                    "",
                    "| Chip | Primary window | Backup | Target | Uplift | Confidence |",
                    "|---|---|---|---|---:|---|",
                ]
            )
            for target in plan.chip_targets:
                primary = (
                    "Unassigned"
                    if target.primary_event_id is None
                    else f"GW{target.primary_event_id}"
                )
                backup = (
                    "None"
                    if target.backup_event_id is None
                    else f"GW{target.backup_event_id}"
                )
                lines.append(
                    f"| {target.chip} | {primary} | {backup} | "
                    f"{target.target_player or '—'} | {target.projected_uplift:.1f} | "
                    f"{target.confidence} |"
                )
            lines.extend(["", "### Chip-window reasoning", ""])
            lines.extend(
                f"- **{target.chip}:** {target.rationale}"
                for target in plan.chip_targets
            )
        lines.extend(["", "## Changes since the previous saved plan", ""])
        lines.extend(f"- {change}" for change in plan.changes)
        lines.extend(["", f"> {plan.methodology}"])
    lines.extend(["", "## Validation", ""])
    lines.extend(f"- {item}" for item in recommendation.validation)
    lines.extend(
        [
            "",
            "> Recommendation only: confirm team news and make any changes yourself in FPL.",
            "",
        ]
    )
    return "\n".join(lines)
