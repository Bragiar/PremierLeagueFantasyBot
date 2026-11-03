**FPL audit — reassessment warranted. Duplicate GW9 deliveries are recorded; no current GW10 action is validated.**

**Review time:** 2026-11-03 08:00:09.800332 UTC.  
**Newest reviewed decision:** 2026-10-31 10:12:32.476026 UTC.  
**Evidence:** supplied code/configuration/tests, truncated decision log, seven settled forecasts through GW8, saved GW9 recommendations/plans, squad reconciliation and previous audit; opened official web pages. **Tests were reviewed as text and have NOT been run. No commands, application API calls, edits or messages were made.**

New evidence includes two GW9 sends, revised squad data and GW8 settlement.

**Delivery and evidence findings**

- **High severity; High confidence — duplicate successful delivery records.** `gw9:120m` appears twice with `delivery: sent`: the 09:00 record recommends `transfer:368:68`; the 10:12 record recommends `transfer:8:115`. The notification map retains only the latter timestamp. This establishes conflicting successful-send records; it does not establish why the duplicate guard was bypassed. Investigate invocation flags, state preservation and runner logs before the next production run. Add coverage for sequential same-key sends and crash recovery; retain Telegram message receipts and distinguish uncertain delivery from definite failure.

- **High severity; High confidence — starting-state reconciliation remains incomplete.** The squad was reconciled at **31 October 09:49:53**, superseding the earlier GW9 decision’s ownership assumptions: Szoboszlai and Calvert-Lewin were already absent. However, it still contains Calafiori, £0.7m and one free transfer, so it does not confirm execution of the later De Cuyper recommendation. No actual-transfer-history file is supplied. Reconcile subsequent user actions before generating GW10 options.

- **Medium severity; High confidence — stale research artifact.** `latest_codex_review.json` supports the earlier Szoboszlai shortlist. The later run explicitly records a Codex failure and no attached review. Bind research artifacts to decision timestamps and shortlist fingerprints, and label stale artifacts.

The scheduler’s **3 November refresh → 6 November 16:30 UTC** agrees with the packet’s 18:30 deadline. Official fixtures show Everton–Coventry kicking off at 20:00 that Friday; applying the official 90-minute rule also implies 18:30. Python remains the sole production deadline runner, effective offsets are `[120]`, and API review is disabled. [Official fixtures](https://www.premierleague.com/en/news/4675097/all-380-fixtures-for-season-2026-27), [deadline rules](https://www.premierleague.com/en/news/4661029)

**Expired shortlist, finances and lineup**

All supplied immediate options belong to **GW9, whose deadline has passed**. None is endorsed for current execution; the conditional GW10 Tavernier move is not a current shortlist authorization.

| Expired GW9 option | Sale / purchase | Resulting bank |
|---|---:|---:|
| `hold` | — | £0.7m |
| `transfer:8:115` — selected | £5.7m / £5.3m | £1.1m |
| `transfer:94:68` | £6.2m / £6.5m | £0.4m |
| `transfer:8:504` | £5.7m / £5.2m | £1.2m |
| `transfer:212:127` | £4.3m / £5.0m | £0.0m |

Each listed move uses one recorded free transfer with zero hit; holding would carry two into the next week. The selling-price implementation matches official half-profit rounding. Complete contemporary market and resolved-player snapshots are missing, limiting independent verification. [Official transfer rules](https://www.premierleague.com/en/news/4661029)

The selected XI forms a legal **4-4-2**: Tzolakis; Gabriel, De Cuyper, Ajayi, Gvardiol; Mbeumo, B.Fernandes, Schade, Groß; Haaland, Evanilson. Haaland captain and Gabriel vice are distinct starters. Bench: van Ewijk, Hughes, Kusi-Asare; reserve Dubravka.

Code checks squad uniqueness, positional quotas, club limits, sale values and affordability. Recorded validation reports success. **Proposal — Medium severity; High confidence:** independently enforce transfer count, available free transfers and total hits at final validation; current zero-hit safety also depends on candidate-generation constraints.

**Forecasts, minutes and calibration**

These are stored outcomes for **forecast lineups**, not confirmed user scores.

| GW | Forecast | Stored outcome | Forecast minus outcome |
|---:|---:|---:|---:|
| 3 | 83.62 | 44 | +39.62 |
| 4 | 77.30 | 57 | +20.30 |
| 5 | 75.26 | 38 | +37.26 |
| 6 | 67.92 | 42 | +25.92 |
| 7 | 69.33 | 60 | +9.33 |
| 8 | 70.31 | 48 | +22.31 |

Latest-six averages reconcile to **2.79 player-points MAE, 14.5 minutes MAE and +25.79 forecast-XI bias**. Earlier GW2 substantially underpredicted: 42.73 versus 106. GW9 remains unsettled in the packet.

**Medium severity; High confidence:** six recent settled weeks justify a calibration investigation, after checking model versions and forecast provenance. They do not justify specific replacement coefficients. Player MAE includes scouting candidates; settlement omits automatic substitutions and vice-captain fallback. The existing three-consecutive-10-point warning correctly remains inactive because GW7 missed by only 9.33.

Minutes require targeted scrutiny:

- Gvardiol’s GW6/GW7 forecasts of **85.0/74.3** met **24/29** minutes; GW8 then reached 90.
- Schade played **51/45/61** in GW6–8; the subsequent 74.6 estimate needs fresh role evidence.
- Fernandes played zero in GW8 against 88.3 expected; Calafiori played 22 against 84.
- Hughes, Kusi-Asare and Dubravka provide minimal projected cover.

City’s official GW9 lineup confirms Haaland and Gvardiol started; it also lists Groß and De Cuyper starting for Brighton. This updates historical start evidence without establishing future minutes or final FPL scores. [Official lineup](https://live.mancity.com/news/mens/city-v-brighton-match-preview-pl-31-oct-63928793)

**Proposals — Medium severity; High confidence:** model recent starts, substitution patterns and recovery scenarios explicitly. Future projections currently retain availability/news and historical role inputs. Preserve immutable forecast versions: `record_forecast` overwrites a Gameweek, including during dry runs, while existing settlements remain unchanged. Treat set-piece orders and predicted positions as dated opinions until corroborated.

**Conditional rolling assessment**

The saved five-week GW9–13 route is De Cuyper; Tavernier; Van Hecke; Vuskovic; hold. Banks **£1.1/0.8/0.1/0.6/0.6m**, next-week free transfers **1/1/1/1/2**, and zero hits are internally consistent with its assumed starting state.

That state is unconfirmed. Rebuild the route before extending it to GW10–14/15. The £0.1m GW11 buffer is fragile, and minimal bench cover persists. Medium/Medium/Medium/Low/Low provides time-based decay, but confidence should also inherit unresolved squad and minutes uncertainty. Future captain selection uses `_project_week`, which lacks the immediate `_captains` eligibility filter; reuse that filter.

**Chip assessment — every window remains conditional**

| First-half chip | Primary / backup | Assessment |
|---|---|---|
| Wildcard | Unassigned / none | Calendar defect persists despite +42.28 immediate uplift and a reported +19.9 rolling advantage. Neither figure independently establishes chip value. |
| Free Hit | GW19 / GW17 | +15.66; stronger future opportunity remains unproven. GW19 prevents GW20 Free Hit. |
| Bench Boost | GW11 / GW13 | +4.66 is weak; three substitutes retain minimal minutes. Reassess after any rebuild. |
| Triple Captain | GW16 / GW10 | Haaland +10.06 versus expired GW9’s +9.46: a small model difference requiring fresh fitness/workload checks. |

Primaries and listed backups do not collide. Backups are not jointly reserved, and chip activation changes the squad underlying other valuations. All four second-half primary/backup windows are absent; leave them unassigned pending evidence.

**High severity; High confidence — repair Wildcard assessment.** In `_build_chip_targets`, rejecting an ordinary Free Hit window executes `continue`, skipping Wildcard assessment for that week. Isolate that branch and add a regression case. Include detailed Wildcard comparison outputs in audit evidence; they are currently omitted.

First-half chips expire at the **GW19 deadline**, cannot carry over, and only one chip may be played per week. **The previous report’s exact expiry time needs correction:** July guidance says 2 January 13:30, while October’s official schedule moves Leeds–Everton to **1 January 20:00 GMT**. The 90-minute rule therefore implies **1 January 18:30 GMT**; Python should verify the live official deadline rather than hardcode either article’s date. [Chip guidance](https://www.premierleague.com/en/news/4679879/whats-happening-with-fpl-chips-in-202627), [revised festive fixtures](https://www.premierleague.com/en/news/4713230/seven-boxing-day-matches-confirmed-as-festive-fixtures-are-released)

Wildcard/Free Hit preserve saved transfers, are unavailable in a manager’s opening Gameweek and cannot be cancelled after confirmation. Bench Boost/Triple Captain can be cancelled before deadline; consecutive Free Hits are prohibited. **Medium severity; High confidence:** validate opening-week and previous-Free-Hit restrictions against confirmed manager history. [Official chip rules](https://www.premierleague.com/en/news/4661029)

No configuration changes are proposed automatically. Priorities are duplicate-delivery investigation, confirmed squad reconciliation, a fresh GW10 shortlist, and repair of the chip-calendar defect.
