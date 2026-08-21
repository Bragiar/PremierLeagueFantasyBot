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


def render_telegram(recommendation: Recommendation, window: str) -> str:
    deadline = recommendation.event.deadline.strftime("%a %d %b, %H:%M UTC")
    hit = "0" if recommendation.points_hit == 0 else f"-{recommendation.points_hit}"
    lines = [
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
    if recommendation.ai_commentary:
        lines.extend(["", "Optional AI view:", recommendation.ai_commentary])
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
    if recommendation.ai_commentary:
        lines.extend(["", "## Optional OpenAI commentary", "", recommendation.ai_commentary])
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
