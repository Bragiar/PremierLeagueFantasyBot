# FPL strategy review — 29 September 2026

## Review scope

Reviewed the project instructions, strategy configuration, public squad baseline, decision log, latest GW6 recommendation and strategy plan, rolling state, forecast history, delivery state, source/test diffs, and Git history. The newest reviewed decision is `2026-09-25T21:41:38.513338+00:00` (GW6 manual dry run). New evidence since the 22 September audit includes two GW6 dry runs, a 25 September public GW5 squad reconciliation, material planner/scoring changes, and four settled forecast weeks. Focused regression tests pass: 24 tests; `git diff --check` is clean.

## Findings

- The latest selectable IDs are `hold`, `transfer:557:124` (Tzolis → Groß), `transfer:557:94` (Tzolis → Schade), and `transfer:557:69` (Tzolis → Scott). The selected transfer is `hold`; the selected chip is `chip:none`. The packet validates a 15-player squad, position quotas, maximum three per club, £0.0m projected bank, and zero hit. The public baseline has one free transfer, Haaland captain and B.Fernandes vice-captain; it cannot establish whether a GW6 action was subsequently made.
- The engine's `hold` conflicts with its strongest legal shortlist: Tzolis → Groß is rated +8.7 over the five-week objective, with Schade +8.46. The hold rationale preserves flexibility, but the current packet is low confidence and explicitly flags this conflict. Keep `hold` as the engine selection pending deadline evidence; any change must use one of these exact IDs.
- GW6 captaincy is fragile: B.Fernandes is captain and Haaland vice-captain, separated by only 0.43 projected points. Bruno was overpredicted by at least four points in each of the last three settled forecasts. Recheck availability, role and set pieces near the deadline; do not treat the current captain as confirmed user action.
- The 25 September public baseline changes the squad materially from the prior authenticated snapshot: Tzolakis, Ajayi, Gvardiol and Calvert-Lewin are present, while Verbruggen, Diop, Shaw and João Pedro are absent. The public ledger supports the baseline and purchase prices, but public picks cannot reveal later GW6 moves.
- Settled forecast facts are GW2 106 actual vs 42.73 expected, GW3 44 vs 83.62, GW4 57 vs 77.30, and GW5 38 vs 75.26. These are forecasts of engine-selected lineups, not proof of the user's executed XI or captaincy. Four weeks show systematic overprojection risk but remain below the requested 4–6-week calibration threshold for changing weights.

## Rolling route

The saved rolling plan and latest strategy plan now agree and validate as reachable: GW6 hold (1 → 2 free transfers, £0.0m bank), conditional GW7 Tzolis → Schade plus van Ewijk → Thomas (2 → 1, £0.1m), GW8 hold (1 → 2), GW9 hold (2 → 3), then conditional GW10 Tzolakis → Petrović (3 → 3, £0.2m). No unexplained hits are planned. Future moves remain conditional and must be recalculated from the actual squad, prices, availability and team news; they are not confirmed transfers.

The route is legal, but its confidence is limited by weak bench cover: Hughes and Kusi-Asare project for only 8.0 and 4.7 minutes in GW6, while van Ewijk is only 52.2 minutes. The proposed GW7 double move is therefore a useful health route, not a commitment. A Wildcard remains a scenario rather than a promised +37.82-point result.

## Chip calendar

All first-half chips remain available. The current provisional calendar is Wildcard unassigned (low), Free Hit GW17 with GW18 backup (low, +5.41), Bench Boost GW9 with GW8 backup (low, +4.27), and Triple Captain GW7 with GW16 backup (medium, +10.13 on Haaland). No two primary or backup targets collide in the saved calendar. The implementation enforces first-half expiry at GW19 and second-half expiry at GW38, and treats a GW19 first-half Free Hit as having opportunity cost because the next-half Free Hit cannot also be used in GW19; the current GW17/GW18 target avoids that collision. These windows are provisional and should not be used without current fixture, availability and double/blank evidence.

The low Bench Boost uplift and low Free Hit uplift do not justify early use. Triple Captain GW7 has the strongest current rationale, but it is still only a medium-confidence projection and should be compared with later doubles before expiry. Wildcard should be reconsidered after the next deadline when the low-minute bench and attack structure are clearer.

## Delivery and risks

The newest records are dry runs only. Historical telemetry contains one `test_failed`, several `test_sent` records, one production `sent` GW3 record, and three production `sent` records for `gw4:manual`; `state/last_run.json` retains one `gw4:manual` sent key. There is no new production send, fallback, retry or duplicate event after the prior audit, but the repeated GW4 records remain a delivery-integrity risk. The latest dry run does not claim a notification window.

Primary risks are the hold-versus-+8.7 shortlist conflict, Bruno captaincy after repeated overprediction, weak bench minutes, public-baseline uncertainty about GW6 execution, and reliance on sparse early-season forecasts. Do not calibrate strategy weights yet. Proposed improvements are to add a boundary test for the hold-policy conflict, test paired-transfer budget and three-per-club rejection paths, preserve explicit conditional labels in route output, and make notification-key idempotency auditable across retries and manual runs.

No strategy, squad, state, workflow, credentials, source code, tests, recommendation, plan, delivery, commit or push changes were made by this audit beyond this review report and the automation memory.
