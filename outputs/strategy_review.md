# Strategy review

- Review time: 2026-08-28T09:43:53Z
- Newest reviewed decision: 2026-08-22T22:34:34.951874+00:00
- Scope: 0 decision-log entries newer than the prior reviewed timestamp; no newer entries remain.

## Findings

There is no new operational evidence. The two logged records are deterministic, manual Gameweek 2 dry runs: both rolled the transfer, took no hit, selected Haaland as captain, passed position/budget/three-per-club validation, and reported `fallback: false`. The different starting XIs and vice-captains show lineup instability, but there are no actual starts, points, transfer-gain, captaincy-return, or delivery outcomes to evaluate. The 17-test suite passes.

The no-hit, optional-transfer-avoidance, chip-saving, and reliable high-ownership premium-captain defaults still make sense as early-season risk controls, but remain uncalibrated. Availability handling combines official status, chance-of-playing, and news conservatively; however, players with zero minutes/starts receive an ownership-based starter-security proxy, and confidence can still be High when the data does not establish a role. Captain eligibility is conservative at 90% availability, but the low-eligible fallback can still choose from a reduced-availability lineup.

The configured five-Gameweek horizon is within the intended 4–6 range. Fixture weighting (0.45) and defensive-contribution weighting (0.35) are reasonable priors, not measured conclusions. The implementation caps the horizon at six but does not reject values below four; teams with no listed fixtures still receive a one-game base score, so blank-Gameweek handling is not explicit. No decision has exercised transfer selection, a tight bank, purchase-price selling rules, or a transfer-created three-per-club edge.

Fallback frequency is zero in the two records. Fallback behavior has unit and API-outage coverage, but no production-like frequency or reason telemetry exists. Delivery evidence is also absent: both records are `dry_run`, `sent_notifications` is empty, and there are no sent, failed, retried, or duplicate-delivery records. The repeated `gw2:manual` key is expected for dry runs and does not validate live duplicate suppression. Git history still contains only the initial build commit (`22fd960`); current implementation, test, state, log, and generated-artifact changes are uncommitted working-tree changes.

## Risks and proposed improvements

1. Retain `max_points_hit: 0`, optional-transfer avoidance, chip saving, and high-ownership premium captaincy. Collect 4–6 real Gameweeks of predicted versus actual starts, points, captain returns, ownership, and transfer gains before tuning weights or thresholds.
2. Validate the fixture horizon as 4–6, add blank/double-Gameweek regression cases, and ensure a blank is not scored as a normal one-game horizon. Reassess fixture versus defensive-contribution weights against outcomes.
3. Separate availability from starter confidence: treat missing minutes/starts or stale news as uncertainty, downgrade confidence accordingly, and test captain/vice-captain behavior when fewer than two players meet the availability threshold.
4. Exercise the full transfer path with non-null purchase prices, a tight bank, a profitable price rise, and an incoming player that would breach the three-per-club limit. Include malformed transfer-price inputs in validation tests.
5. Record structured fallback reasons and attempted/sent/failed/retry/duplicate outcomes; exercise retry and duplicate suppression only in controlled tests. Keep GitHub Actions as the only deadline runner.

Current recommendation: retain the conservative assumptions and monitor the next real scheduled window. No strategy, squad, decision log, state, workflow, credential, source-code, delivery, commit, or push changes were made by this review.
