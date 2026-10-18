# Gameweek 7 recommendation

- **Deadline:** 2026-10-17 10:00 UTC
- **Run window:** 45m
- **Transfers:** Szoboszlai → Groß (£6.8m → £6.1m)
- **Cost / points hit:** 0
- **Captain:** Haaland
- **Vice-captain:** Groß
- **Chip:** None — save the chip
- **Confidence:** Medium
- **Analysis source:** deterministic

## Starting XI

Tzolakis, Gvardiol, Calafiori, Gabriel, Ajayi, van Ewijk, Groß, Mbeumo, B.Fernandes, Schade, Haaland

## Bench

1. Calvert-Lewin, 2. Kusi-Asare, 3. Hughes

Reserve goalkeeper: Dubravka

## Explanation

Use 1 free transfer: Szoboszlai to Groß. The moves remain within budget with £0.8m left and pass all squad rules. Transfers are assessed across the next 5 Gameweeks. The starting XI, bench order and captaincy are assessed separately for this Gameweek because those changes are free. Chip choice: None; estimated uplift 0.0. Risk mode: balanced.

### Confidence notes

- The last three settled forecast XIs overpredicted by at least 10 points each (average 30.5); treat optimizer gains cautiously. These are forecast lineups, not confirmed user results.
- Starting XI contains availability doubts: Schade.
- Wildcard comparison: WC GW7; unrestricted leads the selected no-chip route by +30.3 model score; later chip value is unpriced. See outputs/latest_wildcard_review.md before choosing a chip.

## Current-Gameweek projections

Expected points are model estimates; expected minutes express role uncertainty rather than guaranteed playing time.

| Player | Role | Expected minutes | Expected points |
|---|---|---:|---:|
| Haaland | Captain | 88 | 9.26 |
| Groß | Vice-Captain | 87 | 8.68 |
| Gvardiol | Starter | 74 | 6.17 |
| Mbeumo | Starter | 87 | 5.91 |
| B.Fernandes | Starter | 88 | 5.78 |
| Calafiori | Starter | 83 | 5.67 |
| Gabriel | Starter | 88 | 4.79 |
| Tzolakis | Starter | 86 | 4.60 |
| Ajayi | Starter | 83 | 3.19 |
| van Ewijk | Starter | 72 | 3.12 |
| Schade | Starter | 62 | 2.90 |
| Calvert-Lewin | Bench | 84 | 2.82 |
| Kusi-Asare | Bench | 5 | 0.27 |
| Hughes | Bench | 8 | 0.11 |
| Dubravka | Reserve Goalkeeper | 5 | 0.28 |
| De Cuyper | Transfer Candidate | 82 | 8.54 |
| Dewsbury-Hall | Transfer Candidate | 87 | 5.50 |
| Szoboszlai | Transfer Candidate | 18 | 0.26 |

## Engine shortlist

- **Roll the free transfer** (`hold`): projected gain +0.0. Preserves flexibility and avoids acting on a marginal projection.
- **Szoboszlai → Groß** (`transfer:368:124`) — selected: projected gain +17.9. The move improves the projected best XI plus weighted bench by 17.9 over the configured horizon; incoming availability is 100%. Price timing: Szoboszlai projects -116% toward a fall; that fall would cut the selling price by £0.1m. Groß projects 190% toward a rise, so waiting could add £0.1m to the buying price.
- **Szoboszlai → Dewsbury-Hall** (`transfer:368:236`): projected gain +14.1. The move improves the projected best XI plus weighted bench by 14.1 over the configured horizon; incoming availability is 100%. Price timing: Szoboszlai projects -116% toward a fall; that fall would cut the selling price by £0.1m.
- **Schade → Groß** (`transfer:94:124`): projected gain +13.1. The move improves the projected best XI plus weighted bench by 13.1 over the configured horizon; incoming availability is 100%. Price timing: Schade projects -135% toward a fall; that fall would cut the selling price by £0.1m. Groß projects 190% toward a rise, so waiting could add £0.1m to the buying price.
- **Gvardiol → De Cuyper** (`transfer:391:115`): projected gain +3.2. The move improves the projected best XI plus weighted bench by 3.2 over the configured horizon; incoming availability is 100%. Price timing: De Cuyper projects 166% toward a rise, so waiting could add £0.1m to the buying price. Market-watch candidate: De Cuyper has 883,345 net transfers in this Gameweek; that momentum does not add to the points projection.

## Chip shortlist

- **None** (`chip:none`) — selected: projected uplift +0.0. Preserve the first-half chips for a stronger opportunity before GW19.
- **Triple Captain** (`chip:triple_captain`): projected uplift +9.3. Adds one extra copy of Haaland's projected 9.3 points.
- **Bench Boost** (`chip:bench_boost`): projected uplift +3.5. The four substitutes project for 3.5 points in total.
- **Free Hit** (`chip:free_hit`): projected uplift +20.4. Bounded one-Gameweek legal squad search compared with the current best XI.
  - Optimized squad: Haaland, Rushworth, Kinsky, Tarkowski, De Cuyper, Dasilva, Giles, O'Shea, Semenyo, Cunha, Palmer, Cherki, Groß, Kostoulas, Delap
- **Wildcard** (`chip:wildcard`): projected uplift +51.7. Bounded permanent-squad search across the configured planning horizon.
  - Optimized squad: Haaland, Trafford, Verbruggen, Calafiori, De Cuyper, Dasilva, Guéhi, Tarkowski, Semenyo, McGinn, Rogers, Groß, Tonali, Barry, João Pedro

## Rolling short-term plan

Combined model score over the 5-Gameweek route: **350.3**. This is a comparative rating, not a literal points forecast.

| GW | Transfers | Captain | Chip | Hit | Free transfers after | Bank | Model score | Confidence |
|---:|---|---|---|---:|---:|---:|---:|---|
| 7 | Szoboszlai → Groß | Haaland | None | 0 | 1 | £0.8m | 69.3 | Medium |
| 8 | Ajayi → Dasilva | Haaland | None | 0 | 1 | £1.0m | 69.3 | Medium |
| 9 | Schade → Dewsbury-Hall | Haaland | None | 0 | 1 | £0.6m | 65.0 | Medium |
| 10 | Dubravka → Verbruggen | Haaland | None | 0 | 1 | £0.0m | 73.7 | Low |
| 11 | Roll / no transfer | Haaland | None | 0 | 2 | £0.0m | 73.1 | Low |

### Gameweek 7 projected team

- **Starting XI:** Tzolakis, Gvardiol, Calafiori, Gabriel, Ajayi, van Ewijk, Groß, Mbeumo, B.Fernandes, Schade, Haaland
- **Bench:** Calvert-Lewin, Kusi-Asare, Hughes; reserve goalkeeper Dubravka
- **Reasoning:** Current reviewed action; later weeks are optimized from this legal state.

### Gameweek 8 projected team

- **Starting XI:** Tzolakis, Gabriel, Calafiori, Gvardiol, Dasilva, B.Fernandes, Mbeumo, Groß, Schade, Haaland, Calvert-Lewin
- **Bench:** van Ewijk, Hughes, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Conditional route: the moves improve remaining-horizon player ratings by 4.3.

### Gameweek 9 projected team

- **Starting XI:** Tzolakis, Gvardiol, Gabriel, Calafiori, Dasilva, B.Fernandes, Dewsbury-Hall, Mbeumo, Groß, Haaland, Calvert-Lewin
- **Bench:** van Ewijk, Hughes, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Conditional route: the moves improve remaining-horizon player ratings by 7.2.

### Gameweek 10 projected team

- **Starting XI:** Verbruggen, Gabriel, Calafiori, Gvardiol, Dasilva, B.Fernandes, Dewsbury-Hall, Mbeumo, Groß, Haaland, Calvert-Lewin
- **Bench:** van Ewijk, Kusi-Asare, Hughes; reserve goalkeeper Tzolakis
- **Reasoning:** Conditional route: the moves improve remaining-horizon player ratings by 8.5.

### Gameweek 11 projected team

- **Starting XI:** Verbruggen, Gabriel, Gvardiol, Calafiori, Dasilva, van Ewijk, B.Fernandes, Groß, Dewsbury-Hall, Mbeumo, Haaland
- **Bench:** Calvert-Lewin, Hughes, Kusi-Asare; reserve goalkeeper Tzolakis
- **Reasoning:** Roll to preserve transfer flexibility.

## Provisional long-term chip calendar

These are decision gates, not chips already applied to the short-term route. If one is activated, the route will be rebuilt from the resulting squad.

| Chip | Primary window | Backup | Target | Uplift | Confidence |
|---|---|---|---|---:|---|
| Wildcard | Unassigned | None | — | 0.0 | Low |
| Free Hit | GW18 | GW17 | — | 7.2 | Low |
| Bench Boost | GW11 | GW12 | — | 7.4 | Low |
| Triple Captain | GW16 | GW19 | Haaland | 10.0 | Low |

### Chip-window reasoning

- **Wildcard:** No credible current window; reassess after the next deadline.
- **Free Hit:** One-Gameweek optimized squad compared with the planned route squad.
- **Bench Boost:** Projected points from the four substitutes in the route squad.
- **Triple Captain:** One extra copy of Haaland's captain projection in a home fixture against a promoted club.

## Changes since the previous saved plan

- No material transfer, captain or chip-window changes since the saved plan.

> Bounded rolling-horizon search using current prices and projections; future actions are provisional and recalculated every run.

## Validation

- 15-player squad and position quotas valid
- Maximum three players per club valid
- Transfer budget valid; projected bank £0.8m
- Points hit 0
- Selected reviewed engine option transfer:368:124
- Selected legal chip option chip:none
- Projection sanity bounds passed
- Mini-league risk mode balanced
- Reachable 5-Gameweek rolling route validated
- Recent forecast calibration: 2.99 points MAE and 18.2 minutes MAE across 5 Gameweeks

> Recommendation only: confirm team news and make any changes yourself in FPL.
