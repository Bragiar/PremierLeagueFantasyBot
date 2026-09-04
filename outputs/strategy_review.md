# Strategy review

- Review time: 2026-09-01T23:27:43Z
- Newest reviewed decision: 2026-08-29T23:27:10.917678+00:00
- Evidence scope: 9 newer decision-log records; authenticated squad sync at 2026-08-30T13:23:20.234906+00:00; projection/forecast, planner, transfer-validation, auth/sync and workflow changes through 2026-08-30; current saved route and chip calendar.

## Findings

The current immediate decision is legal on paper: selected transfer `transfer:423:279` (Shaw → Ajayi), selected chip `chip:none`, 0 points hit, projected bank £0.5m, and 2 free transfers before and after the transfer. The recommendation reports valid 15-player/position quotas, budget, maximum-three-per-club, projection-sanity, balanced-risk and reachable-route checks. The GW3 XI has 11 players, three substitutes and a reserve goalkeeper; Ajayi is captain and Haaland vice-captain. All future transfers remain conditional in the generated plan.

The authenticated read-only squad sync still shows Shaw in the squad, bank £0.0m, 2 free transfers, B.Fernandes captain and João Pedro vice-captain. This is evidence of the saved squad before the GW3 deadline, not proof of the user's eventual action; no user-followed transfer or lineup outcome can be inferred from the public/API records.

The newer log contains one `test_failed`, three `test_sent`, and seven `dry_run` records. The failure was followed by successful controlled test deliveries, but repeated `gw2:manual` and `gw2:3h` notification keys show only test/dry-run activity and do not establish production duplicate suppression. `state/last_run.json` has no sent notifications, and no fallback recommendation was recorded. No settled forecasts or official outcomes are present (`state/forecast_history.json` has an empty `settled` map), so transfer gains, starts, points and captain returns cannot yet calibrate the model.

The recent implementation changes materially improve forecast persistence, projection bounds, authenticated squad/purchase-price syncing and focused test coverage. The full test suite passes: 56 tests. The current squad has exact purchase prices and element IDs, which improves selling-value legality, but the new sync/auth path has not produced a settled outcome or production delivery evidence.

## Rolling-plan assessment

`outputs/latest_strategy_plan.json` is a five-Gameweek, 0-hit route with legal projected squads and no unexplained hits: GW3 Shaw → Ajayi, conditional GW4 Hughes → Armstrong, conditional GW5 Verbruggen → Tzolakis, then rolls in GW6–7. It carries 2 free transfers through GW5 and grows to 4 by GW7, with bank £0.5m after GW3 and £0.0m thereafter. Confidence appropriately decays to Low in the early-evidence context, although the GW3 captain choice of Ajayi is a high-impact, low-confidence exposure (65 expected minutes; 10.24 projected points).

There is a material saved-state mismatch. `state/rolling_plan.json` retains the earlier route projections, one free transfer before/after the GW3 action, total projected score 320.31, and Bench Boost primary GW9; the latest output uses two free transfers, total 319.83, and Bench Boost primary GW15. The route should be treated as unresolved until one canonical artifact is regenerated or reconciled. The current latest output is the more recent decision packet, but this review does not overwrite the older state.

## Chip-calendar assessment

The latest provisional calendar is: Wildcard unassigned; Free Hit GW17 with GW18 backup; Bench Boost GW15 with GW6 backup; Triple Captain GW7 with GW16 backup on Haaland. Primary windows do not collide, and the route itself uses no chip. These are conditional decision gates, not confirmed moves.

The code correctly partitions first-half chips through GW19, second-half chips through GW38, preserves Free Hit on GW1, models one-chip-per-Gameweek assignment, and applies a GW19 Free Hit opportunity-cost penalty because a GW19 first-half Free Hit prevents another Free Hit in GW20. However, the tests cover chip availability and collision heuristics but do not directly assert the GW19/GW20 restriction or half-season expiry boundary. The low-confidence uplift estimates (Free Hit +10.2, Bench Boost +7.1, Triple Captain +9.8; Wildcard 0.0) are not strong enough to justify early use, so saving chips remains the appropriate current verdict.

## Risks and proposed improvements

1. Reconcile `outputs/latest_strategy_plan.json` and `state/rolling_plan.json` before relying on the rolling route; add a consistency check that rejects stale generated artifacts with different free-transfer state, chip targets or route changes.
2. Keep the immediate choice conservative: `transfer:423:279` and `chip:none` remain the selected legal IDs, but verify Ajayi's start and role before the deadline. Do not treat the conditional GW4/GW5 moves or chip windows as commitments.
3. Add direct tests for GW19 Free Hit versus GW20 availability, first/second-half chip expiry, and chip assignment when a candidate window is at a boundary. Preserve the one-chip-per-Gameweek rule.
4. Keep strategy weights unchanged. There are only two projected Gameweeks and no settled outcomes; wait for 4–6 completed Gameweeks before calibrating fixture, defensive-contribution, availability or captaincy weights.
5. Extend delivery telemetry to distinguish attempted, failed, retried, sent and duplicate-suppressed outcomes in production-like controlled tests. Retain GitHub Actions as the only deadline runner and production Telegram sender.

Current verdict: the latest GW3 packet passes the available legality checks, but confidence is Low and the rolling-plan artifact mismatch is the highest-priority operational risk. No strategy, squad, log, state, workflow, credential, source-code, test, recommendation, plan, delivery, commit or push changes were made by this review.
