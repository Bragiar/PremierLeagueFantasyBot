**FPL audit — retain `hold` + `chip:none` provisionally; confidence Low.**

**Review time:** 2026-10-20 07:00:09 UTC.  
**Newest recorded decision:** 2026-10-17 09:41:58.531697 UTC, GW7 dry run. The GW8 preview has no generation timestamp.  
**Scope:** supplied squad, code, tests, truncated delivery log, forecasts, saved/preview plans and previous audit; supporting web pages opened. **Tests were reviewed as text and were not run.** No commands, application API calls, edits or messages were performed.

Reassessment is warranted: new deployment metadata resolves the previous scheduling evidence gap, newer official injury news affects recovery assumptions, and serious defects remain unresolved.

**Immediate shortlist and legality**

The current transfer IDs are exactly `hold`, `transfer:368:124`, `transfer:368:236` and `transfer:368:156`. Retain `hold` pending refreshed deadline evidence. Available chip IDs are `chip:none`, `chip:triple_captain`, `chip:bench_boost`, `chip:free_hit` and `chip:wildcard`; retain `chip:none`.

The supplied squad records **£0.1m bank and one free transfer**. Holding costs zero points and leaves two free transfers next week, assuming no intervening user changes. The proposed XI is a legal **5-3-2**, with Haaland captain and Schade vice-captain, both starters. Bench: Kusi-Asare, Hughes, Szoboszlai; reserve goalkeeper Dubravka.

Code checks squad quotas, duplicates, club limits, selling prices and affordability. The selling-price formula matches the official half-profit rule. However, current resolved club IDs, market prices and alternative-transfer price breakdowns are missing, so their legality remains packet-reported. The historical GW7 calculation—£0.1m + £6.8m − £6.1m = £0.8m—is correct but does not establish execution. [Official rules](https://www.premierleague.com/en/news/4661029)

**Findings and proposed improvements**

- **High severity; High confidence — Wildcard calendar defect persists.** In `planner._build_chip_targets`, rejecting an unsuitable Free Hit executes `continue`, skipping that week’s Wildcard analysis. Restrict the rejection to Free Hit processing and add a regression test. “Wildcard unassigned / 0.0” is unreliable alongside the immediate **+52.9** estimate.

- **High severity; High confidence — forecast metrics remain inconsistent.** The supplied five settled weeks yield **2.92 player-points MAE and 16.8 minutes MAE**, versus **2.99/18.2** displayed. GW6’s stored forecast-XI outcome is **42**, whereas the research review implies 34. Generate metrics from one versioned snapshot and preserve immutable forecasts; `record_forecast` currently overwrites a Gameweek, including with dry runs.

- **Medium severity; High confidence — recovery assumptions need updating.** Liverpool’s **19 October** update says Szoboszlai’s injury has not worsened and requires patience, without establishing a return date. A doubtful GW8 appearance is plausible; zero availability throughout five weeks is unsupported. Add conditional recovery scenarios before trusting the +15.8 replacement gain. [Official Liverpool update](https://www.liverpoolfc.com/news/injury-news-jeremie-frimpong-dominik-szoboszlai-liverpool-fc)

- **Medium severity; High confidence — minutes and confidence need stronger evidence.** Schade’s shoulder concern requires refreshed confirmation before retaining him as vice-captain. His 75-minute estimate and Gvardiol’s 67 are model assumptions. Haaland’s reassuring 17 October fitness comments support provisional captaincy, with another European match still relevant. [Brentford update](https://www.brentfordfc.com/en/news/first-team-news-brentford-v-liverpool-premier-league-kevin-schade-jannik-schuster), [City reaction](https://www.mancity.com/matchday/fixtures/mens/2026/premier-league/man-city-v-ipswich-17-oct-2026)

- **Medium severity; High confidence — refresh explanations and validation.** The “more than five days away” note is stale: approximately **3 days 10½ hours** remain. Explain the timing policy directly instead of calling +15.8 marginal. Preserve supplied `element_id` values rather than resolving names fuzzily. Explicitly enforce opening-Gameweek chip restrictions and consecutive-Free-Hit eligibility.

The new metadata confirms effective offsets **`[120]`**, API review disabled, and a scheduler refresh at **06:00 UTC today**, with the next wakeup **23 October, 15:30 UTC**—two hours before the packet’s deadline. This resolves the previous configuration evidence gap. Python remains the sole production deadline runner.

**Forecasts versus outcomes**

These are stored outcomes for recommended lineups, **not confirmed user scores**:

| GW | Forecast | Stored outcome | Forecast minus outcome |
|---:|---:|---:|---:|
| 2 | 42.73 | 106 | −63.27 |
| 3 | 83.62 | 44 | +39.62 |
| 4 | 77.30 | 57 | +20.30 |
| 5 | 75.26 | 38 | +37.26 |
| 6 | 67.92 | 42 | +25.92 |

Forecast-XI MAE is **37.27 points**; the last three overpredictions average **27.83**, not 30.5. Settlement omits automatic substitutions and vice-captain fallback, and “starter hit rate” includes tracked candidates.

Five settled weeks justify a calibration investigation after reconciling versions and forecast timing; they do not establish new coefficients. GW7 remains unsettled in the packet. The GW7 recommendation differs from the confirmed squad, and no actual-transfer ledger is supplied: user execution remains unknown.

**Conditional rolling and chip assessment**

The GW8–12 route remains: hold; Szoboszlai → Dewsbury-Hall; Schade → Groß plus Gvardiol → De Cuyper; Ajayi → Vuskovic; hold. Its **2/2/1/1/2** free-transfer sequence is internally consistent, with zero hits and banks **£0.1/0.3/0.9/0.0/0.0m**.

This is a five-week conditional route. Prices and availability remain fixed; confidence rises from Low to Medium mechanically before decaying to Low. Propagate unresolved starting-state uncertainty instead. The eventual three Brighton players reach the club limit, and £0.0m leaves no price buffer. Historical set-piece evidence supports Groß and De Cuyper, while the Scout’s rotation concerns are analysis, not confirmed future minutes. [Scout analysis](https://www.premierleague.com/en/news/4728140/is-it-still-a-good-idea-invest-in-brighton-players-in-fpl)

| Chip | Primary / backup | Assessment |
|---|---|---|
| Wildcard | Unassigned / none | Repair calendar defect; reconcile +52.9 static uplift with reported +22.9 rolling advantage. Detailed counterfactual output is missing. |
| Free Hit | GW19 / GW17 | +13.3 versus +17.1 now; future superiority is unproven. GW19 prevents another Free Hit in GW20. |
| Bench Boost | GW11 / GW12 | +3.6 is weak; current +0.6 and minimal bench minutes argue for reassessment after improving cover. |
| Triple Captain | GW16 / GW9 | +10.1 versus +9.2 now; Haaland–Hull merits conditional consideration, subject to fitness and minutes. |

Assigned primaries and listed backups do not collide. Backups are not jointly reserved; moving any window requires rebuilding the calendar. No verified Blank/Double Gameweek evidence establishes a stronger window.

First-half chips expire at the **GW19 deadline, 2 January 2027, 13:30 GMT**; the second set covers GW20–38. Only one chip may be used per week. Wildcard/Free Hit preserve saved transfers, are unavailable in a manager’s opening Gameweek and cannot be cancelled once confirmed. Bench Boost/Triple Captain can be cancelled before deadline. No second-half windows are supplied. [Official chip guidance](https://www.premierleague.com/en/news/4679879/whats-happening-with-fpl-chips-in-202627), [Official rules](https://www.premierleague.com/en/news/4661029)

**Delivery assessment**

The visible log contains **one successful send and two dry runs**; repeated `gw7:45m` dry runs are not duplicate deliveries. No failure is visible. Truncation prevents a complete audit, and the GW8 preview has no delivery record.

**Medium severity; High confidence:** successful delivery precedes saving notification state, leaving a crash/ambiguous-timeout duplicate risk. Persist attempt identifiers and Telegram receipts, distinguish uncertain delivery from definite failure, and add recovery tests. No configuration changes are proposed automatically.
