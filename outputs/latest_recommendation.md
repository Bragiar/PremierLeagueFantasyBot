# Gameweek 6 recommendation

- **Deadline:** 2026-10-10 10:00 UTC
- **Run window:** manual
- **Transfers:** Roll / no transfer
- **Cost / points hit:** 0
- **Captain:** B.Fernandes
- **Vice-captain:** Haaland
- **Chip:** None — save the chip
- **Confidence:** Low
- **Analysis source:** deterministic

## Starting XI

Tzolakis, Gabriel, Calafiori, Gvardiol, Ajayi, B.Fernandes, Mbeumo, Tzolis, Szoboszlai, Haaland, Calvert-Lewin

## Bench

1. van Ewijk, 2. Kusi-Asare, 3. Hughes

Reserve goalkeeper: Dubravka

## Explanation

Roll the transfer. No urgent availability problem clears the configured multi-fixture gain threshold, so a points-free hold is preferred. Transfers are assessed across the next 5 Gameweeks. The starting XI, bench order and captaincy are assessed separately for this Gameweek because those changes are free. Chip choice: None; estimated uplift 0.0. Risk mode: balanced.

### Confidence notes

- The model overestimated B.Fernandes by at least 4 points in each of three recent forecasts (average 7.9); recheck captaincy near the deadline.
- Only 5 completed Gameweeks of current-season evidence.
- Captaincy is close: the top-two model margin is only 0.43 points.
- The hold policy conflicts with a shortlisted model gain of 8.7.

## Current-Gameweek projections

Expected points are model estimates; expected minutes express role uncertainty rather than guaranteed playing time.

| Player | Role | Expected minutes | Expected points |
|---|---|---:|---:|
| B.Fernandes | Captain | 89 | 8.96 |
| Haaland | Vice-Captain | 89 | 8.44 |
| Mbeumo | Starter | 88 | 7.11 |
| Gabriel | Starter | 88 | 6.13 |
| Calafiori | Starter | 83 | 5.44 |
| Gvardiol | Starter | 85 | 5.36 |
| Tzolakis | Starter | 86 | 5.26 |
| Ajayi | Starter | 83 | 3.95 |
| Tzolis | Starter | 76 | 3.83 |
| Szoboszlai | Starter | 86 | 3.64 |
| Calvert-Lewin | Starter | 83 | 2.92 |
| van Ewijk | Bench | 52 | 1.50 |
| Kusi-Asare | Bench | 5 | 0.27 |
| Hughes | Bench | 8 | 0.20 |
| Dubravka | Reserve Goalkeeper | 5 | 0.06 |
| Groß | Transfer Candidate | 87 | 7.58 |
| Schade | Transfer Candidate | 86 | 6.92 |
| Scott | Transfer Candidate | 86 | 4.92 |

## Engine shortlist

- **Roll the free transfer** (`hold`) — selected: projected gain +0.0. Preserves flexibility and avoids acting on a marginal projection.
- **Tzolis → Groß** (`transfer:557:124`): projected gain +8.7. The move improves the projected best XI plus weighted bench by 8.7 over the configured horizon; incoming availability is 100%.
- **Tzolis → Schade** (`transfer:557:94`): projected gain +8.5. The move improves the projected best XI plus weighted bench by 8.5 over the configured horizon; incoming availability is 100%.
- **Tzolis → Scott** (`transfer:557:69`): projected gain +5.6. The move improves the projected best XI plus weighted bench by 5.6 over the configured horizon; incoming availability is 100%.

## Chip shortlist

- **None** (`chip:none`) — selected: projected uplift +0.0. Preserve the first-half chips for a stronger opportunity before GW19.
- **Triple Captain** (`chip:triple_captain`): projected uplift +9.0. Adds one extra copy of B.Fernandes's projected 9.0 points.
- **Bench Boost** (`chip:bench_boost`): projected uplift +2.0. The four substitutes project for 2.0 points in total.
- **Free Hit** (`chip:free_hit`): projected uplift +17.6. Bounded one-Gameweek legal squad search compared with the current best XI.
  - Optimized squad: Tzolakis, Verbruggen, Davis, Thomas, Hall, Tarkowski, Branthwaite, B.Fernandes, Groß, Schade, Mbeumo, Barnes, Emersonn, Haaland, Barry
- **Wildcard** (`chip:wildcard`): projected uplift +37.8. Bounded permanent-squad search across the configured planning horizon.
  - Optimized squad: Tzolakis, Raya, Guéhi, Gvardiol, Hall, Tarkowski, Virgil, Scott, Grimes, Groß, Schade, Saka, Emersonn, Kostoulas, Haaland

## Rolling short-term plan

Combined model score over the 5-Gameweek route: **356.4**. This is a comparative rating, not a literal points forecast.

| GW | Transfers | Captain | Chip | Hit | Free transfers after | Bank | Model score | Confidence |
|---:|---|---|---|---:|---:|---:|---:|---|
| 6 | Roll / no transfer | B.Fernandes | None | 0 | 2 | £0.0m | 70.0 | Medium |
| 7 | Tzolis → Schade, van Ewijk → Thomas | Haaland | None | 0 | 1 | £0.1m | 73.0 | Medium |
| 8 | Roll / no transfer | Haaland | None | 0 | 2 | £0.1m | 73.2 | Medium |
| 9 | Roll / no transfer | Haaland | None | 0 | 3 | £0.1m | 67.7 | Low |
| 10 | Tzolakis → Petrović | Haaland | None | 0 | 3 | £0.2m | 72.5 | Low |

### Gameweek 6 projected team

- **Starting XI:** Tzolakis, Gabriel, Calafiori, Gvardiol, Ajayi, B.Fernandes, Mbeumo, Tzolis, Szoboszlai, Haaland, Calvert-Lewin
- **Bench:** van Ewijk, Kusi-Asare, Hughes; reserve goalkeeper Dubravka
- **Reasoning:** Current reviewed action; later weeks are optimized from this legal state.

### Gameweek 7 projected team

- **Starting XI:** Tzolakis, Gvardiol, Gabriel, Calafiori, Ajayi, Thomas, B.Fernandes, Mbeumo, Szoboszlai, Schade, Haaland
- **Bench:** Calvert-Lewin, Kusi-Asare, Hughes; reserve goalkeeper Dubravka
- **Reasoning:** Conditional route: the moves improve remaining-horizon player ratings by 10.4.

### Gameweek 8 projected team

- **Starting XI:** Tzolakis, Gabriel, Gvardiol, Calafiori, Thomas, B.Fernandes, Schade, Mbeumo, Szoboszlai, Haaland, Calvert-Lewin
- **Bench:** Ajayi, Hughes, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 9 projected team

- **Starting XI:** Tzolakis, Gvardiol, Gabriel, Ajayi, Calafiori, B.Fernandes, Schade, Mbeumo, Szoboszlai, Haaland, Calvert-Lewin
- **Bench:** Thomas, Hughes, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 10 projected team

- **Starting XI:** Petrović, Gabriel, Calafiori, Gvardiol, Thomas, B.Fernandes, Mbeumo, Szoboszlai, Schade, Haaland, Calvert-Lewin
- **Bench:** Ajayi, Kusi-Asare, Hughes; reserve goalkeeper Dubravka
- **Reasoning:** Conditional route: the moves improve remaining-horizon player ratings by 2.3.

## Provisional long-term chip calendar

These are decision gates, not chips already applied to the short-term route. If one is activated, the route will be rebuilt from the resulting squad.

| Chip | Primary window | Backup | Target | Uplift | Confidence |
|---|---|---|---|---:|---|
| Wildcard | Unassigned | None | — | 0.0 | Low |
| Free Hit | GW17 | GW18 | — | 5.4 | Low |
| Bench Boost | GW9 | GW8 | — | 4.3 | Low |
| Triple Captain | GW7 | GW16 | Haaland | 10.1 | Medium |

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
- Transfer budget valid; projected bank £0.0m
- Points hit 0
- Selected reviewed engine option hold
- Selected legal chip option chip:none
- Projection sanity bounds passed
- Mini-league risk mode balanced
- Reachable 5-Gameweek rolling route validated
- Recent forecast calibration: 3.01 points MAE and 16.7 minutes MAE across 4 Gameweeks

> Recommendation only: confirm team news and make any changes yourself in FPL.
