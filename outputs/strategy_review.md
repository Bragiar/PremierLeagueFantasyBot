# FPL strategy review — 6 October 2026

## Review scope

Reviewed `AGENTS.md`, strategy configuration, squad baseline, decision log, latest GW6 recommendation and plan, rolling state, forecast history, delivery state, relevant source/test changes, working-tree diff, and Git history. New evidence since the 29 September review is the 1 October planner/scoring/deadline-alert release and regenerated GW6 packet/state, plus uncommitted auth/CLI fallback changes. The newest reviewed decision remains `2026-09-25T21:41:38.513338+00:00` (`gw6:manual` dry run). No user execution is inferred after that timestamp.

Focused regression tests for deadlines, planner, engine options, evaluation, fallback, duplicate prevention, and Telegram pass: 23 tests.

## Findings

- The current legal immediate shortlist is `hold`, `transfer:557:124` (Tzolis → Groß, +8.7), `transfer:557:94` (Tzolis → Schade, +8.5), and `transfer:557:69` (Tzolis → Scott, +5.6). The selected IDs remain `hold` and `chip:none`; validation reports a legal 15-player squad, budget, maximum-three-per-club rule, £0.0m bank, and zero hit. Any real action must be one of these exact current IDs.
- The new early-transfer hold policy explains why `hold` is selected while the stronger transfer shortlist is still displayed. This is internally coherent but remains a material decision conflict: the current plan is low confidence and should be revisited only with late availability/role evidence. The public squad baseline is not proof that GW6 was played as shown.
- The current XI is Tzolakis, Gabriel, Calafiori, Gvardiol, Ajayi, B.Fernandes, Mbeumo, Tzolis, Szoboszlai, Haaland and Calvert-Lewin; bench order is van Ewijk, Kusi-Asare, Hughes, with Dubravka in reserve. It is structurally valid, but bench cover is weak: the packet projects about 52, 5 and 8 minutes for those three substitutes.
- Captaincy remains fragile: B.Fernandes leads Haaland by only 0.43 projected points. The new confidence warning cites three consecutive recent captain overestimates averaging 7.9 points. Keep this as a deadline review risk, not evidence of a user-selected captain.

## Outcomes and calibration

Officially settled engine forecasts available are GW2 actual 106 vs expected 42.73, GW3 44 vs 83.62, GW4 57 vs 77.30, and GW5 38 vs 75.26. Mean points MAE is 3.01 and mean minutes MAE is 16.66 across four settled weeks. These compare engine-selected forecast lineups, not confirmed user actions. Four weeks are still below the configured 4–6-week calibration threshold; do not change weights yet. The repeated Bruno overprediction is enough to lower confidence and prompt deadline review, but not enough to recalibrate strategy.

## Rolling route

The saved plan files are byte-identical and validate as reachable: GW6 hold (1 → 2 free transfers, £0.0m), conditional GW7 Tzolis → Schade plus van Ewijk → Thomas (2 → 1, £0.1m), GW8 hold (1 → 2), GW9 hold (2 → 3), then conditional GW10 Tzolakis → Petrović (3 → 3, £0.2m). All planned hits are zero and the route preserves legal squad structure. Every move after GW6 is conditional and must be rebuilt from the actual squad, prices, availability and news; none is a confirmed future transfer. Confidence decays to Low by GW9–10, appropriately reflecting projection uncertainty.

The 1 October planner changes—two-transfer bundles, all-outgoing search, stronger minutes gates, bench weighting, form smoothing and future-prior blending—are directionally sensible and now covered by focused tests. They make the hold-vs-transfer conflict more visible, but the report should continue to distinguish comparative model score from literal points.

## Chip calendar

The provisional calendar remains Wildcard unassigned (Low), Free Hit GW17 with GW18 backup (Low, +5.4), Bench Boost GW9 with GW8 backup (Low, +4.3), and Triple Captain GW7 with GW16 backup (Medium, +10.1 on Haaland). No primary/backup collision is present in the saved targets. The implementation retains first-half expiry at GW19, second-half availability through GW38, and the GW19 first-half Free Hit opportunity-cost restriction; the current GW17/GW18 Free Hit target avoids that collision.

The low Bench Boost and Free Hit uplifts do not justify early use. Triple Captain GW7 has the strongest current rationale, but it remains conditional and should be compared with later double-gameweek evidence before activation. Wildcard remains a decision gate, not a planned move. A chip activation would require rebuilding the route from the resulting squad.

## Delivery, source changes and risks

Decision-log telemetry totals 13 dry runs, 6 sent records, 3 test-sent records and 1 test-failed record. There is no new production send, fallback, retry, or post-25-September decision. Historical repeated `gw4:manual` sent records remain a duplicate/idempotency risk, although `state/last_run.json` retains one sent key.

The uncommitted auth/CLI changes add a local macOS auth-file fallback and catch Keychain lookup errors before environment fallback. They do not alter strategy decisions or production delivery in this audit; keep credentials outside the repository and do not commit secrets. The 1 October committed deadline change broadens notification windows to tolerate delayed scheduled runs; it is covered by the passing deadline tests but still cannot recover a run that never starts before the deadline.

Specific improvements:

- Add an explicit regression test and report warning for the policy case where `hold` is selected while a legal transfer exceeds the configured conflict threshold.
- Keep outcome settlement separate from execution attribution, and add GW6 settlement before considering calibration.
- Make duplicate notification-key history and retry provenance auditable rather than relying on the single latest state key.
- Recheck captaincy and the Tzolis transfer shortlist near the deadline using official availability and role news; do not turn the rolling route or chip calendar into confirmed actions.

No strategy, squad, state, workflow, credentials, source code, tests, recommendation, plan, delivery, commit or push changes were made by this audit beyond this review report and the automation memory.
