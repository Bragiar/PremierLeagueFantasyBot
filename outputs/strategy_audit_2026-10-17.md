# Strategy and Wildcard audit — 17 October 2026

## Verdict

The old no-Haaland Wildcard was a search result, not evidence that selling Haaland was required. The corrected, broader search finds a stronger legal draft retaining him. Early Wildcards deserve explicit testing. Do not infer that a default no-chip selection numerically beats the tested alternatives: the saved early-chip policy still requires review.

## Findings and changes

1. **Early chips were suppressed by policy.** `save_chips_by_default=true` plus `allow_exceptional_early_chip=false` returns no chip before expiry pressure, even above the exceptional gain threshold. Automatic selection is still conservative, but `wildcard_review_enabled=true` now generates a common-horizon comparison on normal live-data runs. It compares the exact selected immediate shortlist action and a hold, with ordinary transfers or a GW8 Wildcard, plus a Wildcard now. No comparison activates a chip or sends Telegram.
2. **Wildcard objectives used a single aggregate lineup/captain.** Chip rebuilds now sum separate weekly legal lineup and captain objectives. Future fixture swings can change who starts and captains, rather than assuming one five-week XI.
3. **Both local searches shared the same cheap seed.** The optimizer now tries premium anchors across positions and an eligible existing-squad seed, as well as absolute/value upgrade searches. The separate report also explicitly tests retaining the selected captain at the rebuild. Bounded search still does not establish global optimality. The original no-Haaland draft materially understated the explored options.
4. **Retained players were charged market repurchase prices.** Chip budgets now use the selling opportunity cost for retained holdings, preserving their existing purchase basis. Their unrealized profit no longer disappears merely because a chip is modelled. Updated throughout immediate chip budgets, route initialization, scheduled rebuilds and calendar searches.
5. **Confidence missed some real risks.** A flagged starter now prevents an unqualified High rating even if availability-adjusted expected minutes exceed 55. A separate warning catches three consecutive large forecast-XI overestimates independently of the current captain. The latest three misses average 30.5 points. These describe forecast lineups, not verified user scores, and do not automatically change model weights.
6. **Chip reports incorrectly described a rebuild as rolling a transfer.** Wildcard and Free Hit outputs now say squad rebuild, and no longer apply a misleading hold-policy conflict to the rebuild.

## Current tests on the tracked squad

Five-week comparative scores from the updated search:

| Route | Model score | Difference vs Gross + ordinary transfers |
|---|---:|---:|
| Wildcard now, retaining Haaland | 380.67 | +30.34 |
| Szoboszlai to Gross, Wildcard GW8 | 361.81 | +11.48 |
| Szoboszlai to Gross, ordinary transfers | 350.33 | 0.00 |

The current improved immediate `chip:wildcard` draft passes the complete Python recommendation flow, with zero hit, £0.3m bank, Haaland captain and Semenyo vice. It is saved separately as `gw7_wildcard_validated.md/json`. Latest no-chip recommendation and comparison outputs are regenerated separately. Neither a transfer nor a chip has been submitted to FPL.

The proposed Wildcard squad is Trafford, Verbruggen; Calafiori, De Cuyper, Dasilva, Guéhi, Tarkowski; Semenyo, McGinn, Rogers, Gross, Tonali; Haaland, Barry, João Pedro. This is a legal model draft, not a fully news-reviewed endorsement of every role or bench choice. In particular, current projections still hold future player availability and roles fixed, and Gross may remain selected even through difficult fixtures. Do not treat that as independent verification of his future role or returns.

## Sensitivity checks

Using one official data snapshot and the same immediate shortlist, Wildcard now led the selected ordinary-transfer route by +27.87 over four weeks and +31.04 over six weeks. Increasing the immediate/weekly fixture weight from 1.0 to 1.5 in an experiment produced a +34.01 advantage. Gross then GW8 Wildcard remained positive in each case (+9.08, +11.63, +13.45 respectively). These are scenario checks, not historical backtests. Saved scoring weights and the five-week horizon remain unchanged.

## How to interpret this

All route totals are comparative model scores, not guaranteed additional points. A no-chip route retains its Wildcard, and its value outside the comparison horizon is not priced. Four- to six-week checks share the same underlying model and are not independent evidence of accuracy. Current roles, injury flags and prices are static, and uncertain recovery or rotation can change rankings. Ordinary transfers after a rebuild remain reachable, legal, bounded plans rather than free independent dream teams. At a future Wildcard, the comparison rebuilds from the strongest limited set of prefix states (default one); increasing the configured state searches broadens this.

Enumerating every possible squad is unnecessary and computationally wasteful. More diverse constrained search addresses the demonstrated local-search weakness. An exact mixed-integer solver could later certify the optimum for a precisely specified objective, but would not repair inaccurate projections. We should not mistake optimizer precision for forecasting accuracy.

Keep balanced risk mode, no routine points hits, and explicit chip review. Test Wildcard timing more aggressively; do not tune form, fixture, minutes or underlying-stat weights to fit these five settled weeks. Before weight changes, collect/replay deadline-time input snapshots and evaluate chronologically on held-out weeks, tracking points bias, minutes error, starter hit rate and captain outcomes. Historical projections alone cannot fully reconstruct old player pools and news without look-ahead bias.

Official rules reference: https://www.premierleague.com/es/news/4661029 (banked free transfers retained through Wildcard/Free Hit). Chip expiry reference: https://www.premierleague.com/en/news/4679879/whats-happening-with-fpl-chips-in-202627 .

## Verification

73 tests pass, including new coverage for weekly captain rotation, required captain retention, appreciated-player budgets, scheduled Wildcard legality and transfer carryover, unavailable chips, comparison non-mutation, rebuild wording, and repeated forecast bias. Full live no-OpenAI previews exercised both no-chip and exact shortlisted Wildcard paths. No OpenAI API request or Telegram delivery was used. Existing unrelated working-tree edits were preserved.
