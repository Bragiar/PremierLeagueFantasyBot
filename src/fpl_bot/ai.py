from __future__ import annotations

import json
import os
from typing import Any

from fpl_bot.models import Recommendation


def add_optional_ai_commentary(
    recommendation: Recommendation, config: dict[str, Any]
) -> tuple[bool, str | None]:
    """Add prose only; deterministic selections remain the source of truth."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or not bool(config.get("enabled", True)):
        return False, None

    try:
        from openai import OpenAI

        model = os.getenv("OPENAI_MODEL", "gpt-5.6-sol").strip() or "gpt-5.6-sol"
        client = OpenAI(api_key=api_key, timeout=25.0, max_retries=1)
        context = recommendation.to_dict()
        response = client.responses.create(
            model=model,
            reasoning={"effort": str(config.get("reasoning_effort", "low"))},
            instructions=(
                "You are a cautious Fantasy Premier League analyst. Explain the supplied "
                "validated deterministic plan in no more than three concise sentences. "
                "Do not alter transfers, captaincy, lineup, bench, chip, costs, or rules. "
                "State uncertainty plainly and do not claim access to private team data."
            ),
            input=json.dumps(context, ensure_ascii=False, separators=(",", ":")),
        )
        commentary = response.output_text.strip()
        limit = int(config.get("max_explanation_characters", 700))
        if commentary:
            recommendation.ai_commentary = commentary[:limit]
            recommendation.source = "deterministic+openai"
            return True, None
        return False, "OpenAI returned no commentary"
    except Exception as exc:  # The deterministic plan must survive every AI failure.
        return False, f"{type(exc).__name__}: optional commentary unavailable"
