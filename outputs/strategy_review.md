# Strategy review

- Review time: 2026-09-08T21:47:48Z
- Newest reviewed decision: 2026-09-04T14:53:06.307738+00:00
- Evidence scope: one decision after the prior review; settled GW2 forecast outcome; authenticated squad baseline; current recommendation, rolling plan and chip calendar; delivery state; source/test history through 2026-09-04.

## Findings

The latest immediate packet selected exact legal IDs `hold` and `chip:none`: no transfer, 0 points hit, projected bank £0.0m, and 2 free transfers before the action. Its validation reports valid squad/position quotas, maximum-three-per-club, budget, projection bounds, and a reachable five-Gameweek route. The GW3 XI has 11 players, three ordered substitutes, reserve goalkeeper Dubravka, B.Fernandes captain and Haaland vice-captain. The engine shortlist is the complete selectable set for that packet; no action outside it is endorsed.

The authenticated squad file remains a pre-deadline baseline: Shaw is still present, bank is £0.0m, free transfers are 2, and the saved captain/vice-captain are B.Fernandes/João Pedro. This does not prove whether the user followed the recommendation or changed the team before the deadline.

One settled forecast outcome is now available for GW2. The recorded forecast expected 42.73 team points, with 88.9% expected-starter hit rate, 22.111 minutes MAE and 3.465 points MAE; the stored official outcome is 106 team points. The large points gap is dominated by outcome variance and the B.Fernandes captain return in the record, but one Gameweek is insufficient to recalibrate weights. The public/API data still cannot establish the user's actual submitted XI or captain.

Delivery evidence now includes one production `sent` record (`gw3:3h`) and `state/last_run.json` records that notification. Earlier evidence remains one `test_failed`, three `test_sent`, and seven `dry_run` records. No fallback was recorded, and there is no production retry or duplicate. Repeated older notification keys were test/dry-run activity, so they are not evidence of production duplication.

The previously reported mismatch between `outputs/latest_strategy_plan.json` and `state/rolling_plan.json` is resolved in the current artifacts: route, free-transfer state, chip targets and projected total are aligned at 358.05 across the five-Gameweek plan. The latest recommendation's saved route is therefore the current canonical packet, subject to recalculation at the next review.

## Rolling-plan assessment

The route is structurally reachable and contains no unexplained hits: GW3 rolls, GW4 conditionally considers Diop → Thomas, and GW5–7 roll. Free transfers progress 2 → 3 → 3 → 4 → 5 → 5, with bank £0.0m throughout. Later actions and captaincy are provisional, not confirmed moves. Confidence is Medium for GW3–5 and Low for GW6–7; this is appropriate given sparse evidence, but the immediate hold conflicts with a shortlisted 19.9 model gain. Shaw, Diop and Tzolis have only about 64–66 expected minutes in the current packet, so role/start news remains a material risk before any future decision.

## Chip-calendar assessment

The selected current chip is `chip:none`. The provisional calendar is Wildcard unassigned; Free Hit GW17 with GW18 backup; Bench Boost GW13 with GW8 backup; and Triple Captain GW7 with GW16 backup on Haaland. Primary windows do not collide, and all future windows remain conditional. The current packet's chip shortlist is legal and includes the exact available IDs only.

The implementation preserves first-half chips through GW19, second-half chips after that boundary, enforces one chip per Gameweek in the planner, and applies the GW19 Free Hit opportunity-cost logic. However, focused tests still do not directly assert the GW19/GW20 Free Hit restriction, half-season expiry boundary, or a boundary collision. Current uplift estimates (Free Hit 41.9, Wildcard 219.2, Triple Captain 12.7, Bench Boost 2.2) are model outputs rather than reliable reasons to spend a chip; saving remains the defensible current policy until fixture and availability evidence strengthens.

## Risks and proposed improvements

1. Keep `hold` and `chip:none` as the audited current selections, but do not infer that they were executed. Rebuild from a fresh authenticated squad state before treating any future transfer or captaincy as current.
2. Add direct boundary tests for GW19/GW20 Free Hit availability, first/second-half expiry, and one-chip-per-Gameweek collisions.
3. Add a consistency check that rejects stale route artifacts if the latest plan and saved rolling state diverge again.
4. Keep strategy weights unchanged. Reassess after at least 4–6 completed Gameweeks; the single settled outcome is useful monitoring evidence but not calibration evidence.
5. Extend delivery telemetry to distinguish attempted, failed, retried, sent and duplicate-suppressed production outcomes. Keep GitHub Actions as the only deadline runner and production Telegram sender.

Current verdict: the latest sent GW3 packet is internally legal and the saved route is now consistent, but confidence remains Medium/Low and user execution is unknown. No strategy, squad, log, state, workflow, credential, source-code, test, recommendation, plan, delivery, commit or push changes were made by this audit.
