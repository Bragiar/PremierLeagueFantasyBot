**FPL audit — retain `hold` + `chip:none` provisionally; decision confidence Low.**

**Review time:** 2026-10-18 10:28:32 UTC.  
**Newest recorded decision:** 2026-10-17 09:41:58.531697 UTC, GW7 dry run. The newer GW8 preview has no generation timestamp.  
**Scope:** supplied code, tests, truncated decision log, squad, forecasts and plans; supporting official web pages opened. Tests were reviewed as text and **were not run**. No commands, API calls, edits or messages were performed. No previous audit report was supplied, so `NO_CHANGE` cannot be established.

**Immediate decision and legality**

The current transfer shortlist is exactly `hold`, `transfer:368:124`, `transfer:368:236` and `transfer:368:156`. Retain `hold`; preserve chips with `chip:none`. The other current chip IDs are `chip:triple_captain`, `chip:bench_boost`, `chip:free_hit` and `chip:wildcard`. No alternative has sufficient verified evidence to justify changing the selection now.

The supplied squad records £0.1m bank and one free transfer. Holding leaves £0.1m, costs zero points and produces two free transfers next week under the supplied model. The GW8 XI is a legal 5-3-2, with distinct starting captain Haaland and vice-captain Schade. Bench: Kusi-Asare, Hughes, Szoboszlai; reserve goalkeeper Dubravka.

Code checks squad quotas, duplicate players, club limits, selling prices and affordability. Its selling-price formula matches the official half-profit rule. However, current market prices, resolved club IDs and full GW8 transfer price details are absent: **current transfer affordability and club counts remain packet-reported, not independently verified**. The earlier GW7 £6.8m sale/£6.1m purchase correctly leaves £0.8m from £0.1m. That recommendation is not proof the user executed it. [Official rules](https://www.premierleague.com/en/news/4661029)

**Findings and proposed improvements**

- **High — Wildcard calendar can be skipped incorrectly. Confidence High.** In `planner._build_chip_targets`, rejecting a Free Hit candidate executes `continue`, bypassing the subsequent Wildcard analysis for that week. This can explain “Wildcard unassigned / 0.0” despite the immediate +52.9 estimate. Restrict that rejection to Free Hit processing and add a regression case where Free Hit is unsuitable but Wildcard remains assessable.

- **High — forecast evidence is inconsistent across artifacts. Confidence High.** From the supplied settled GW2–6 history, player-points MAE averages **2.92**, minutes MAE **16.8**; the GW8 output instead reports 2.99/18.2. GW6 forecast-XI outcome is **42**, not the 34 implied by the web review’s claimed 34-point miss. Correct the review and derive all displayed metrics from one timestamped, versioned snapshot.

- **High — production configuration cannot be verified. Confidence High in the evidence gap.** The scheduler requires `[120]`, while supplied base configuration contains `[1440,180,45]`; local overrides and scheduler status are excluded. This does not prove production is misconfigured. Include sanitized effective notification settings, runtime location, scheduler status and deployment revision in future packets. Python should remain the sole production deadline runner.

- **Medium — minutes and recovery assumptions need scenario handling. Confidence High.** Future projections retain current injury status and largely season-average minutes. An injured player can therefore remain unavailable throughout the horizon without recovery evidence. Add recovery/rotation scenarios and evidence-age confidence limits. Liverpool confirms Szoboszlai’s recurrence and need for further recovery, without a return date. [Official Liverpool update](https://www.liverpoolfc.com/news/andoni-iraola-on-jeremie-frimpong-and-dominik-szoboszlai-injuries)

- **Medium — explanations and confidence overstate precision. Confidence High.** Calling the transfer marginal conflicts with the shortlisted +15.8 gain; the operative reason is the early-transfer timing policy. Explain that directly. GW9–10 “Medium” confidence also follows a Low-confidence starting decision with unresolved ownership, injuries and prices; propagate those uncertainties through the route.

- **Medium — strengthen validation and audit coverage. Confidence High.** `load_squad` discards supplied `element_id`, then resolves names fuzzily; preserve stable IDs. Enforce opening-Gameweek Wildcard restrictions and the consecutive-Free-Hit prohibition explicitly. Add focused tests for these rules, the Wildcard calendar defect, settlement substitutions and interrupted delivery.

**Forecasts versus outcomes**

These are reconstructed outcomes for **forecast lineups**, not confirmed user scores:

| GW | Forecast | Stored outcome | Forecast minus outcome |
|---:|---:|---:|---:|
| 2 | 42.73 | 106 | −63.27 |
| 3 | 83.62 | 44 | +39.62 |
| 4 | 77.30 | 57 | +20.30 |
| 5 | 75.26 | 38 | +37.26 |
| 6 | 67.92 | 42 | +25.92 |

Forecast-XI MAE is **37.27 points**; the last three overpredictions average **27.83**, rather than the displayed 30.5. Settlement omits automatic substitutions and vice-captain fallback, so its “actual team points” label needs qualification.

Five settled weeks justify investigating calibration, but changing coefficients requires reconciling versions and forecast timing first. Preserve immutable forecast records: `record_forecast` currently overwrites each Gameweek, including with dry runs. Separate starters from scouting candidates in metrics; the reported starter hit rate currently includes candidates. GW7 remains unsettled in the supplied history.

**Conditional rolling and chip assessment**

The GW8–12 route is: hold; Szoboszlai → Dewsbury-Hall; Schade → Groß plus Gvardiol → De Cuyper; Ajayi → Vuskovic; hold. Its free-transfer sequence **2/2/1/1/2** is internally consistent, with zero hits and nonnegative banks. Recalculate from the actual squad before each deadline; the £0.0m endpoint leaves no price buffer. Buying three Brighton players also warrants refreshed role evidence: the Scout documented congestion and competition for places, but its October 1 analysis is not current lineup confirmation. [Scout analysis](https://www.premierleague.com/en/news/4728140/is-it-still-a-good-idea-invest-in-brighton-players-in-fpl)

| Chip | Primary / backup | Assessment |
|---|---|---|
| Wildcard | Unassigned / none | Calendar defect undermines this result. Reconcile +52.9 static uplift with the reported +22.9 rolling comparison; detailed counterfactual output is missing. |
| Free Hit | GW19 / GW17 | +13.3 is uncertain and below the current +17.1 estimate. Compare both explicitly; GW19 blocks another Free Hit in GW20. |
| Bench Boost | GW11 / GW12 | +3.6 is weak; current bench projects only +0.6. Reassess after improving playing cover. |
| Triple Captain | GW16 / GW9 | +10.1 versus +9.2 now. GW16’s Haaland–Hull fixture supports consideration, conditional on fitness and role. |

Assigned primaries and listed backups have no collisions, but Wildcard is missing and backups are not jointly reserved. Rebuild the calendar whenever a chip moves. Officially, only one chip may be used per Gameweek; first-half chips expire at the **GW19 deadline, 2 January 2027, 13:30 GMT**, and second-half chips cover GW20–38. Wildcard/Free Hit preserve banked transfers; both are unavailable for a manager’s opening Gameweek and cannot be cancelled once confirmed. Bench Boost/Triple Captain can be cancelled before deadline. [Official rules](https://www.premierleague.com/en/news/4661029), [2026/27 chip guidance](https://www.premierleague.com/en/news/4679879/whats-happening-with-fpl-chips-in-202627)

Haaland’s post-match fitness comments support provisional captaincy, not guaranteed minutes. Schade’s vice-captain role needs fresh fitness confirmation. [Official City reaction](https://www.mancity.com/matchday/fixtures/mens/2026/premier-league/man-city-v-ipswich-17-oct-2026)

**Delivery assessment**

The visible log contains one successful send and two dry runs; repeated `gw7:45m` dry runs are **not duplicate deliveries**. No failure is visible, but truncation prevents a complete delivery audit. The latest GW8 preview has no delivery record, consistent with preview behavior.

A remaining **Medium-severity, High-confidence** reliability risk is delivery succeeding before notification state is saved: a crash or ambiguous timeout can trigger a duplicate retry. Persist attempt IDs and returned message receipts, distinguish uncertain delivery from definite failure, and test recovery. No automatic configuration changes are proposed.
