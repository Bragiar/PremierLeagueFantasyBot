# Gameweek 5 recommendation

- **Deadline:** 2026-09-18 17:30 UTC
- **Run window:** 45m
- **Transfers:** Shaw → Ajayi (£4.4m → £4.2m)
- **Cost / points hit:** 0
- **Captain:** Haaland
- **Vice-captain:** B.Fernandes
- **Chip:** None — save the chip
- **Confidence:** High
- **Analysis source:** deterministic

## Starting XI

Verbruggen, Calafiori, Ajayi, Gabriel, Diop, B.Fernandes, Mbeumo, Szoboszlai, Tzolis, Haaland, João Pedro

## Bench

1. van Ewijk, 2. Kusi-Asare, 3. Hughes

Reserve goalkeeper: Dubravka

## Explanation

Use one free transfer: Shaw to Ajayi. The move remains within budget with £0.2m left and passes all squad rules. Transfers are assessed across the next 5 Gameweeks. The starting XI, bench order and captaincy are assessed separately for this Gameweek because those changes are free. Chip choice: None; estimated uplift 0.0. Risk mode: balanced.

### Confidence notes

- Stable expected minutes and clear model margins.

## Current-Gameweek projections

Expected points are model estimates; expected minutes express role uncertainty rather than guaranteed playing time.

| Player | Role | Expected minutes | Expected points |
|---|---|---:|---:|
| Haaland | Captain | 89 | 10.27 |
| B.Fernandes | Vice-Captain | 87 | 8.23 |
| Calafiori | Starter | 80 | 7.73 |
| Ajayi | Starter | 78 | 7.19 |
| Gabriel | Starter | 86 | 6.84 |
| Mbeumo | Starter | 85 | 6.78 |
| João Pedro | Starter | 65 | 5.62 |
| Szoboszlai | Starter | 85 | 5.44 |
| Tzolis | Starter | 74 | 4.12 |
| Verbruggen | Starter | 82 | 3.84 |
| Diop | Starter | 82 | 2.75 |
| van Ewijk | Bench | 82 | 2.23 |
| Kusi-Asare | Bench | 9 | 0.19 |
| Hughes | Bench | 11 | 0.00 |
| Dubravka | Reserve Goalkeeper | 10 | 0.34 |
| Tavernier | Transfer Candidate | 82 | 7.12 |
| Giles | Transfer Candidate | 81 | 6.69 |
| Davis | Transfer Candidate | 81 | 6.59 |
| Shaw | Transfer Candidate | 31 | 0.40 |

## Engine shortlist

- **Roll the free transfer** (`hold`): projected gain +0.0. Preserves flexibility and avoids acting on a marginal projection.
- **Diop → Giles** (`transfer:259:282`): projected gain +19.9. Engine scores Giles 19.9 points above Diop over the configured horizon; incoming availability is 100%.
- **Tzolis → Tavernier** (`transfer:557:68`): projected gain +19.7. Engine scores Tavernier 19.7 points above Tzolis over the configured horizon; incoming availability is 100%.
- **Diop → Davis** (`transfer:259:305`): projected gain +18.9. Engine scores Davis 18.9 points above Diop over the configured horizon; incoming availability is 100%.
- **Shaw → Ajayi** (`transfer:423:279`) — selected: projected gain +34.3. The deterministic safety policy selected this legal move for an availability risk; projected gain is 34.3.

## Chip shortlist

- **None** (`chip:none`) — selected: projected uplift +0.0. Preserve the first-half chips for a stronger opportunity before GW19.
- **Triple Captain** (`chip:triple_captain`): projected uplift +10.3. Adds one extra copy of Haaland's projected 10.3 points.
- **Bench Boost** (`chip:bench_boost`): projected uplift +2.8. The four substitutes project for 2.8 points in total.
- **Free Hit** (`chip:free_hit`): projected uplift +27.0. Bounded one-Gameweek legal squad search compared with the current best XI.
  - Optimized squad: Raya, Verbruggen, Guéhi, Gvardiol, Maitland-Niles, Tarkowski, Bogle, Saka, Gakpo, George Hemmings, Gibbs-White, Groß, Thomas-Asante, Simms, Haaland
- **Wildcard** (`chip:wildcard`): projected uplift +143.5. Bounded permanent-squad search across the configured planning horizon.
  - Optimized squad: Tzolakis, Raya, Tarkowski, Gvardiol, De Cuyper, Ajayi, Bogle, Saka, Scott, Schade, Groß, Tavernier, Haaland, Isak, Emersonn

## Rolling short-term plan

Combined model score over the 5-Gameweek route: **368.4**. This is a comparative rating, not a literal points forecast.

| GW | Transfers | Captain | Chip | Hit | Free transfers after | Bank | Model score | Confidence |
|---:|---|---|---|---:|---:|---:|---:|---|
| 5 | Shaw → Ajayi | Haaland | None | 0 | 2 | £0.2m | 79.1 | High |
| 6 | Diop → Giles, Verbruggen → Tzolakis | Haaland | None | 0 | 1 | £0.1m | 72.3 | Medium |
| 7 | Roll / no transfer | Haaland | None | 0 | 2 | £0.1m | 73.4 | Medium |
| 8 | Tzolis → Schade, João Pedro → Thiago | Haaland | None | 0 | 1 | £0.2m | 72.8 | Low |
| 9 | Roll / no transfer | Haaland | None | 0 | 2 | £0.2m | 70.8 | Low |

### Gameweek 5 projected team

- **Starting XI:** Verbruggen, Calafiori, Ajayi, Gabriel, Diop, B.Fernandes, Mbeumo, Szoboszlai, Tzolis, Haaland, João Pedro
- **Bench:** van Ewijk, Kusi-Asare, Hughes; reserve goalkeeper Dubravka
- **Reasoning:** Current reviewed action; later weeks are optimized from this legal state.

### Gameweek 6 projected team

- **Starting XI:** Tzolakis, Gabriel, Calafiori, Ajayi, Giles, B.Fernandes, Mbeumo, Tzolis, Szoboszlai, Haaland, João Pedro
- **Bench:** van Ewijk, Kusi-Asare, Hughes; reserve goalkeeper Dubravka
- **Reasoning:** Conditional route: the moves improve remaining-horizon player ratings by 12.5.

### Gameweek 7 projected team

- **Starting XI:** Tzolakis, Gabriel, Calafiori, Ajayi, Giles, B.Fernandes, Mbeumo, Szoboszlai, Tzolis, Haaland, João Pedro
- **Bench:** van Ewijk, Kusi-Asare, Hughes; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 8 projected team

- **Starting XI:** Tzolakis, Gabriel, Calafiori, Ajayi, van Ewijk, B.Fernandes, Schade, Szoboszlai, Mbeumo, Haaland, Thiago
- **Bench:** Giles, Hughes, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Conditional route: the moves improve remaining-horizon player ratings by 6.4.

### Gameweek 9 projected team

- **Starting XI:** Tzolakis, Gabriel, Ajayi, Giles, Calafiori, B.Fernandes, Schade, Mbeumo, Szoboszlai, Haaland, Thiago
- **Bench:** van Ewijk, Hughes, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

## Provisional long-term chip calendar

These are decision gates, not chips already applied to the short-term route. If one is activated, the route will be rebuilt from the resulting squad.

| Chip | Primary window | Backup | Target | Uplift | Confidence |
|---|---|---|---|---:|---|
| Wildcard | Unassigned | None | — | 0.0 | Low |
| Free Hit | GW17 | GW18 | — | 9.8 | Low |
| Bench Boost | GW9 | GW8 | — | 4.9 | Low |
| Triple Captain | GW7 | GW16 | Haaland | 10.1 | Medium |

### Chip-window reasoning

- **Wildcard:** No credible current window; reassess after the next deadline.
- **Free Hit:** One-Gameweek optimized squad compared with the planned route squad.
- **Bench Boost:** Projected points from the four substitutes in the route squad.
- **Triple Captain:** One extra copy of Haaland's captain projection in a home fixture against a promoted club.

## Changes since the previous saved plan

- Advanced the rolling plan from GW3 to GW5.
- GW5 transfer plan changed: Roll / no transfer → Shaw → Ajayi.
- GW6 transfer plan changed: Roll / no transfer → Diop → Giles, Verbruggen → Tzolakis.
- GW6 captain changed: B.Fernandes → Haaland.
- Bench Boost target changed: GW13 → GW9.

> Bounded rolling-horizon search using current prices and projections; future actions are provisional and recalculated every run.

## Validation

- 15-player squad and position quotas valid
- Maximum three players per club valid
- Transfer budget valid; projected bank £0.2m
- Points hit 0
- Selected reviewed engine option transfer:423:279
- Selected legal chip option chip:none
- Projection sanity bounds passed
- Mini-league risk mode balanced
- Reachable 5-Gameweek rolling route validated
- Recent forecast calibration: 3.34 points MAE and 19.2 minutes MAE across 2 Gameweeks

> Recommendation only: confirm team news and make any changes yourself in FPL.
