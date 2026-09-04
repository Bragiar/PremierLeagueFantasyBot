# Gameweek 3 recommendation

- **Deadline:** 2026-09-04 17:30 UTC
- **Run window:** 3h
- **Transfers:** Roll / no transfer
- **Cost / points hit:** 0
- **Captain:** B.Fernandes
- **Vice-captain:** Haaland
- **Chip:** None — save the chip
- **Confidence:** Medium
- **Analysis source:** deterministic

## Starting XI

Verbruggen, Calafiori, Gabriel, Shaw, Diop, B.Fernandes, Szoboszlai, Mbeumo, Tzolis, Haaland, João Pedro

## Bench

1. Hughes, 2. Kusi-Asare, 3. van Ewijk

Reserve goalkeeper: Dubravka

## Explanation

Roll the transfer. No urgent availability problem clears the configured multi-fixture gain threshold, so a points-free hold is preferred. Transfers are assessed across the next 5 Gameweeks. The starting XI, bench order and captaincy are assessed separately for this Gameweek because those changes are free. Chip choice: None; estimated uplift 0.0. Risk mode: balanced.

### Confidence notes

- Only 2 completed Gameweeks of current-season evidence.
- The hold policy conflicts with a shortlisted model gain of 19.9.

## Current-Gameweek projections

Expected points are model estimates; expected minutes express role uncertainty rather than guaranteed playing time.

| Player | Role | Expected minutes | Expected points |
|---|---|---:|---:|
| B.Fernandes | Captain | 83 | 12.68 |
| Haaland | Vice-Captain | 85 | 9.32 |
| Calafiori | Starter | 72 | 9.34 |
| João Pedro | Starter | 81 | 8.57 |
| Szoboszlai | Starter | 75 | 7.69 |
| Mbeumo | Starter | 76 | 7.25 |
| Gabriel | Starter | 77 | 6.11 |
| Verbruggen | Starter | 68 | 4.36 |
| Tzolis | Starter | 64 | 2.35 |
| Shaw | Starter | 64 | 1.88 |
| Diop | Starter | 65 | 1.39 |
| Hughes | Bench | 17 | 0.78 |
| Kusi-Asare | Bench | 17 | 0.78 |
| van Ewijk | Bench | 65 | 0.00 |
| Dubravka | Reserve Goalkeeper | 17 | 0.63 |
| Ndiaye | Transfer Candidate | 69 | 8.02 |
| Ajer | Transfer Candidate | 66 | 6.92 |
| Thomas | Transfer Candidate | 65 | 3.89 |

## Engine shortlist

- **Roll the free transfer** (`hold`) — selected: projected gain +0.0. Preserves flexibility and avoids acting on a marginal projection.
- **Shaw → Ajer** (`transfer:423:87`): projected gain +19.9. Engine scores Ajer 19.9 points above Shaw over the configured horizon; incoming availability is 100%.
- **Tzolis → Ndiaye** (`transfer:557:237`): projected gain +18.9. Engine scores Ndiaye 18.9 points above Tzolis over the configured horizon; incoming availability is 100%.
- **Diop → Thomas** (`transfer:259:173`): projected gain +18.4. Engine scores Thomas 18.4 points above Diop over the configured horizon; incoming availability is 100%.

## Chip shortlist

- **None** (`chip:none`) — selected: projected uplift +0.0. Preserve the first-half chips for a stronger opportunity before GW19.
- **Triple Captain** (`chip:triple_captain`): projected uplift +12.7. Adds one extra copy of B.Fernandes's projected 12.7 points.
- **Bench Boost** (`chip:bench_boost`): projected uplift +2.2. The four substitutes project for 2.2 points in total.
- **Free Hit** (`chip:free_hit`): projected uplift +41.9. Bounded one-Gameweek legal squad search compared with the current best XI.
  - Optimized squad: Tzolakis, Petrović, Kayode, Mendy, Ajayi, De Cuyper, Calafiori, Cherki, Gakpo, M.Sangaré, Saka, B.Fernandes, Thomas-Asante, Simms, Haaland
- **Wildcard** (`chip:wildcard`): projected uplift +219.2. Bounded permanent-squad search across the configured planning horizon.
  - Optimized squad: Tzolakis, Trafford, De Cuyper, Tarkowski, Ajayi, Calafiori, White, Saka, Cherki, B.Fernandes, M.Sangaré, Palmer, Wissa, Barry, João Pedro

## Rolling short-term plan

Combined model score over the 5-Gameweek route: **358.1**. This is a comparative rating, not a literal points forecast.

| GW | Transfers | Captain | Chip | Hit | Free transfers after | Bank | Model score | Confidence |
|---:|---|---|---|---:|---:|---:|---:|---|
| 3 | Roll / no transfer | B.Fernandes | None | 0 | 3 | £0.0m | 83.7 | Medium |
| 4 | Diop → Thomas | Haaland | None | 0 | 3 | £0.0m | 68.5 | Medium |
| 5 | Roll / no transfer | Haaland | None | 0 | 4 | £0.0m | 68.4 | Medium |
| 6 | Roll / no transfer | B.Fernandes | None | 0 | 5 | £0.0m | 69.0 | Low |
| 7 | Roll / no transfer | Haaland | None | 0 | 5 | £0.0m | 68.5 | Low |

### Gameweek 3 projected team

- **Starting XI:** Verbruggen, Calafiori, Gabriel, Shaw, Diop, B.Fernandes, Szoboszlai, Mbeumo, Tzolis, Haaland, João Pedro
- **Bench:** Hughes, Kusi-Asare, van Ewijk; reserve goalkeeper Dubravka
- **Reasoning:** Current reviewed action; later weeks are optimized from this legal state.

### Gameweek 4 projected team

- **Starting XI:** Verbruggen, Gabriel, Calafiori, Thomas, van Ewijk, B.Fernandes, Szoboszlai, Mbeumo, Tzolis, Haaland, João Pedro
- **Bench:** Shaw, Hughes, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Conditional route: the moves improve remaining-horizon player ratings by 4.7.

### Gameweek 5 projected team

- **Starting XI:** Verbruggen, Gabriel, Calafiori, Thomas, Shaw, B.Fernandes, Mbeumo, Szoboszlai, Tzolis, Haaland, João Pedro
- **Bench:** van Ewijk, Hughes, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 6 projected team

- **Starting XI:** Verbruggen, Gabriel, Calafiori, Thomas, van Ewijk, B.Fernandes, Mbeumo, Tzolis, Szoboszlai, Haaland, João Pedro
- **Bench:** Shaw, Kusi-Asare, Hughes; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 7 projected team

- **Starting XI:** Verbruggen, Gabriel, Calafiori, Shaw, Thomas, B.Fernandes, Mbeumo, Szoboszlai, Tzolis, Haaland, João Pedro
- **Bench:** van Ewijk, Kusi-Asare, Hughes; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

## Provisional long-term chip calendar

These are decision gates, not chips already applied to the short-term route. If one is activated, the route will be rebuilt from the resulting squad.

| Chip | Primary window | Backup | Target | Uplift | Confidence |
|---|---|---|---|---:|---|
| Wildcard | Unassigned | None | — | 0.0 | Low |
| Free Hit | GW17 | GW18 | — | 9.9 | Low |
| Bench Boost | GW13 | GW8 | — | 5.2 | Low |
| Triple Captain | GW7 | GW16 | Haaland | 9.8 | Medium |

### Chip-window reasoning

- **Wildcard:** No credible current window; reassess after the next deadline.
- **Free Hit:** One-Gameweek optimized squad compared with the planned route squad.
- **Bench Boost:** Projected points from the four substitutes in the route squad.
- **Triple Captain:** One extra copy of Haaland's captain projection in a home fixture against a promoted club.

## Changes since the previous saved plan

- GW3 transfer plan changed: Shaw → Ajayi → Roll / no transfer.
- GW3 captain changed: Ajayi → B.Fernandes.
- GW4 transfer plan changed: Hughes → Armstrong → Diop → Thomas.
- GW5 transfer plan changed: Verbruggen → Tzolakis → Roll / no transfer.
- GW6 captain changed: Haaland → B.Fernandes.
- Bench Boost target changed: GW9 → GW13.

> Bounded rolling-horizon search using current prices and projections; future actions are provisional and recalculated every run.

## Validation

- 15-player squad and position quotas valid
- Maximum three players per club valid
- Transfer budget valid; projected bank £0.0m
- Points hit 0
- Selected reviewed engine option hold
- Selected legal chip option chip:none
- Projection sanity bounds passed
- Mini-league risk mode balanced
- Reachable 5-Gameweek rolling route validated
- Recent forecast calibration: 3.46 points MAE and 22.1 minutes MAE across 1 Gameweeks

> Recommendation only: confirm team news and make any changes yourself in FPL.
