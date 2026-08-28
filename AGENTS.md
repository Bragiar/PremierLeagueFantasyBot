# FPL project instructions

## In-app review without the bot's OpenAI API

When the user asks to run or review the FPL bot “locally”, “here in Codex/ChatGPT”,
“without the API”, or with similar wording, use this workflow:

1. Do not use `OPENAI_API_KEY` and do not let the Python bot call OpenAI. Generate a
   non-recording engine packet with:

   `.venv/bin/fpl-bot --preview --force --no-openai`

2. Read `outputs/latest_recommendation.md` and `outputs/latest_strategy_plan.json`.
   Treat the immediate transfer and chip shortlists as the complete set of selectable
   actions for the current Gameweek. Do not invent or select a current transfer or chip
   outside those exact option IDs. The later rolling-plan actions are conditional and
   may be discussed or challenged, but must not be presented as confirmed moves.
3. Use the app's own web-search capability to check current, deadline-relevant evidence:
   official availability and press conferences first, then reliable predicted lineups,
   tactical or set-piece role changes, rotation risks, Blank/Double Gameweek prospects,
   chip expiry, and reputable FPL analysis. Cite sources and separate reported facts
   from expert opinion.
4. Challenge the engine rather than merely agreeing with it. State a verdict, confidence,
   risks, the preferred transfer option ID, and the preferred chip option ID. Compare a
   chip's calculated uplift with plausible stronger opportunities before it expires.
   Also review whether the short-term route relies on doubtful starters or outdated role
   assumptions, and whether the provisional primary/backup chip windows still make sense.
   Keep the engine choices unless a different shortlisted combination has high-confidence
   support from at least two recent sources.
5. Finalize through Python so budget and squad rules are checked again. Normally use:

   `.venv/bin/fpl-bot --dry-run --force --no-openai --select-option '<option-id>' --select-chip '<chip-id>'`

   If the user explicitly asks to test Telegram delivery, instead use:

   `.venv/bin/fpl-bot --force --no-openai --select-option '<option-id>' --select-chip '<chip-id>' --test-telegram`

6. Read the regenerated output and report the current decision, short-term route,
   provisional chip calendar, and material changes from the previously saved plan with
   the web evidence in chat.
   Never send Telegram unless the user explicitly requests the test. Test delivery must
   retain the prominent test label and must not claim the real notification window. If web
   research is unavailable or inconclusive, finalize the engine's already-selected option.

This workflow avoids charges to the user's OpenAI API account. It still uses whatever
ChatGPT/Codex plan and usage limits apply to the current app session.
