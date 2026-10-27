**FPL audit — reassessment warranted. No current GW9 action is validated by this packet.**

**Review time:** 2026-10-27 08:00:09 UTC.  
**Newest reviewed decision:** 2026-10-23 15:30:01.164504 UTC, GW8, recorded delivery `sent`.  
**Evidence:** supplied code/configuration/tests, truncated decision log, six settled forecasts through GW7, GW8 recommendation/rolling plan, previous audit, and opened official web pages. **Tests were reviewed as text; this audit ran no tests, commands, application API calls, edits or messages.**

New evidence includes the GW8 production decision and GW7 settlement. The previous report’s provisional GW8 hold is superseded by that recorded decision.

**Immediate shortlist, finances and lineup**

The latest shortlist belongs to **expired GW8**:

- Transfers: `hold`, `transfer:368:124`, `transfer:368:156`, `transfer:368:236`, `transfer:368:68`.
- Chips: `chip:none`, `chip:triple_captain`, `chip:bench_boost`, `chip:free_hit`, `chip:wildcard`.

The recorded selection was `transfer:368:124` plus `chip:none`. Its arithmetic reconciles: **£0.1m bank + £6.8m sale − £6.2m purchase = £0.7m**, using one recorded free transfer, zero hits, and leaving one free transfer for the following week. Alternative transfer banks were £0.4m for Neto, £0.3m for Dewsbury-Hall and £0.7m for Tavernier.

The recommended XI was a legal **5-4-1**: Tzolakis; Calafiori, Gabriel, van Ewijk, Gvardiol, Ajayi; Mbeumo, B.Fernandes, Groß, Schade; Haaland. Captain Haaland and vice Mbeumo both started in the recommended XI. Bench: Calvert-Lewin, Kusi-Asare, Hughes; reserve Dubravka.

Code checks duplicates, position quotas, club limits, selling prices and affordability. The selling-price formula matches official rules. Complete market-price and resolved-club snapshots are absent, so full legality remains dependent on the recorded validation. [Official rules](https://www.premierleague.com/en/news/4661029)

**High severity; High confidence:** `data/squad.yaml` remains confirmed only to **17 October**, still containing Szoboszlai and £0.1m. Neither the GW7 recommendation nor GW8 delivery proves user execution. Reconcile actual squad, purchase/selling prices, bank, transfers and chips before producing a fresh GW9 shortlist. **Do not replay a GW8 ID or promote conditional Evanilson into an immediate action.**

**Findings and proposed improvements**

- **High severity; High confidence — Wildcard calendar defect persists.** In `planner._build_chip_targets`, rejecting an ordinary Free Hit window executes `continue`, bypassing that week’s Wildcard assessment. This can explain “Unassigned / 0.0” despite **+49.23** immediate Wildcard uplift and a reported **+24.6** rolling advantage. Restrict that branch to Free Hit processing and add a regression case proving Wildcard assessment survives.

- **High severity; High confidence — recovery assumptions exaggerate transfer gains.** Future projections retain current availability, news, starts and minutes. Szoboszlai’s current zero availability therefore persists throughout the horizon. Liverpool’s **23 October** update established absence that weekend while describing recovery as close; it did not establish five weeks out. Compare conditional recovery scenarios before trusting the **+19.59** gain. [Liverpool availability update](https://www.liverpoolfc.com/news/liverpools-injury-list-suspensions-and-availability)

- **Medium severity; High confidence — minutes confidence remains too broad.** Gvardiol’s stored GW6/GW7 minutes were **24/29**, against **85.0/74.3** forecasts; Schade played **51/45**, before his estimate rebounded to 75.3. City’s latest report confirms Gvardiol and Haaland started at Villa and Haaland scored. That updates the evidence but does not guarantee future starts. Reassess after the **28 October City–Brighton cup match**. [City report](https://www.mancity.com/news/mens/aston-villa-v-city-premier-league-match-report-63928435)

- **Medium severity; High confidence — preserve reproducible forecasts and evidence.** `record_forecast` overwrites each Gameweek, including through dry runs; settlement is then retained independently. Preserve immutable forecast versions, generation/model timestamps and delivery provenance. Add the referenced Wildcard comparison outputs to the audit allowlist: their detailed results are currently missing.

- **Medium severity; High confidence — enforce chip restrictions explicitly.** Availability flags alone do not establish eligibility: Wildcard lacks an opening-Gameweek guard, and Free Hit eligibility does not consult previous-week use. Validate both against confirmed manager history and test these boundaries.

**Forecasts versus outcomes**

These are **stored outcomes for forecast lineups**, not confirmed user scores.

| GW | Forecast | Stored outcome | Forecast minus outcome |
|---:|---:|---:|---:|
| 2 | 42.73 | 106 | −63.27 |
| 3 | 83.62 | 44 | +39.62 |
| 4 | 77.30 | 57 | +20.30 |
| 5 | 75.26 | 38 | +37.26 |
| 6 | 67.92 | 42 | +25.92 |
| 7 | 69.33 | 60 | +9.33 |

The displayed **2.86 player-points MAE / 15.5 minutes MAE across six weeks now reconciles**. Forecast-XI MAE is **32.62 points**. GW3–7 all overpredicted, averaging **26.49**, but GW7’s 9.33 miss correctly clears the existing three-consecutive-10-point warning.

Six weeks justify a calibration investigation after reconciling forecast versions and differing model implementations; they do not yet justify specific replacement coefficients. Settlement omits automatic substitutions and vice-captain fallback, while “starter hit rate” includes tracked candidates.

**GW8 remains unsettled in the packet.** Official reports confirm Liverpool beat Brighton 2–0, Groß started and scored an own goal; these facts do not establish his final FPL points or the recommended team’s score. Predicted roles and set-piece orders remain opinion until evidenced. [Liverpool report](https://www.liverpoolfc.com/news/match-report-brighton-liverpool-premier-league), [Brighton report](https://www.brightonandhovealbion.com/media-article/mft-match-report-liverpool-bha-pl-october-2026)

**Conditional rolling and chip assessment**

The saved **GW8–12 five-week route** is: Groß transfer; Calvert-Lewin → Evanilson; Dubravka → Verbruggen; Gvardiol → De Cuyper; hold. Recorded banks **£0.7/0.6/0.0/0.4/0.4m**, next-week transfers **1/1/1/1/2**, and zero hits are internally consistent.

It depends on unconfirmed GW8 execution and fixed prices. GW10 has no price buffer; acquiring De Cuyper reaches three Brighton players. Confidence decays Medium/Medium/Medium/Low/Low, but future confidence should also inherit unresolved starting-state and role uncertainty.

| First-half chip | Primary / backup | Assessment |
|---|---|---|
| Wildcard | Unassigned / none | Repair defect; compare refreshed conditional GW9/GW10 rebuilds. Missing detailed counterfactual prevents endorsement. |
| Free Hit | GW19 / GW17 | +11.6 versus expired GW8’s +17.7; stronger future value is unproven. |
| Bench Boost | GW11 / GW12 | +7.8 remains weak; Hughes and Kusi-Asare retain minimal projected minutes. |
| Triple Captain | GW16 / GW9 | Haaland +10.1 versus expired GW8’s +9.7; modest model difference, subject to fitness and workload. |

Listed primaries/backups do not collide. Backups are not jointly reserved; changing one window requires rebuilding the calendar. No verified Blank/Double Gameweek evidence establishes a stronger opportunity.

Each chip has a second copy for GW20–38, but **all four second-half primary/backup windows are missing**. Leave them unassigned pending evidence.

Official season guidance places first-half expiry at the **GW19 deadline, 2 January 2027, 13:30 GMT**; unused chips cannot carry over. Only one chip may be used per week. [2026/27 chip guidance](https://www.premierleague.com/en/news/4679879/whats-happening-with-fpl-chips-in-202627)

Wildcard/Free Hit preserve saved transfers, are unavailable in a manager’s opening Gameweek and cannot be cancelled once confirmed. Bench Boost/Triple Captain can be cancelled before deadline. Consecutive Free Hits are prohibited, so GW19 blocks GW20. [Official rules](https://www.premierleague.com/en/news/4661029)

**Delivery and scheduling**

The visible log contains **one successful GW8 send and two GW7 dry runs**, with no visible failure or duplicate successful send. Truncation prevents a complete delivery audit.

Effective offsets are **`[120]`**, API review is disabled, and the scheduler’s 27 October refresh schedules **31 October 09:00 UTC**, two hours before the packet’s GW9 deadline. Python remains the sole production deadline runner.

**Medium severity; High confidence:** Telegram success precedes durable notification-state saving, leaving crash/ambiguous-timeout duplicate risk. Persist attempt identifiers and Telegram receipts, distinguish uncertain delivery from definite failure, and add recovery coverage. No automatic configuration change is proposed.
