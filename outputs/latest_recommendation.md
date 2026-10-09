# Gameweek 6 recommendation

- **Deadline:** 2026-10-10 10:00 UTC
- **Run window:** 24h
- **Transfers:** Tzolis → Schade (£6.3m → £6.2m)
- **Cost / points hit:** 0
- **Captain:** Haaland
- **Vice-captain:** Schade
- **Chip:** None — save the chip
- **Confidence:** Medium
- **Analysis source:** deterministic

## Starting XI

Tzolakis, Gabriel, Gvardiol, Calafiori, Ajayi, Schade, B.Fernandes, Mbeumo, Szoboszlai, Haaland, Calvert-Lewin

## Bench

1. van Ewijk, 2. Kusi-Asare, 3. Hughes

Reserve goalkeeper: Dubravka

## Explanation

Use 1 free transfer: Tzolis to Schade. The moves remain within budget with £0.1m left and pass all squad rules. Transfers are assessed across the next 5 Gameweeks. The starting XI, bench order and captaincy are assessed separately for this Gameweek because those changes are free. Chip choice: None; estimated uplift 0.0. Risk mode: balanced.

### Confidence notes

- Only 5 completed Gameweeks of current-season evidence.
- Captaincy is close: the top-two model margin is only 0.29 points.

## Current-Gameweek projections

Expected points are model estimates; expected minutes express role uncertainty rather than guaranteed playing time.

| Player | Role | Expected minutes | Expected points |
|---|---|---:|---:|
| Haaland | Captain | 89 | 7.88 |
| Schade | Vice-Captain | 86 | 7.88 |
| B.Fernandes | Starter | 89 | 7.27 |
| Gabriel | Starter | 88 | 6.13 |
| Mbeumo | Starter | 88 | 5.87 |
| Gvardiol | Starter | 85 | 5.52 |
| Calafiori | Starter | 83 | 5.01 |
| Tzolakis | Starter | 86 | 4.61 |
| Szoboszlai | Starter | 86 | 3.44 |
| Ajayi | Starter | 83 | 3.25 |
| Calvert-Lewin | Starter | 83 | 3.18 |
| van Ewijk | Bench | 52 | 1.65 |
| Kusi-Asare | Bench | 5 | 0.27 |
| Hughes | Bench | 8 | 0.20 |
| Dubravka | Reserve Goalkeeper | 5 | 0.06 |
| Groß | Transfer Candidate | 87 | 8.69 |
| Barnes | Transfer Candidate | 86 | 6.33 |
| Tzolis | Transfer Candidate | 57 | 2.54 |

## Engine shortlist

- **Roll the free transfer** (`hold`): projected gain +0.0. Preserves flexibility and avoids acting on a marginal projection.
- **Tzolis → Schade** (`transfer:557:94`) — selected: projected gain +16.3. The move improves the projected best XI plus weighted bench by 16.3 over the configured horizon; incoming availability is 100%.
- **Tzolis → Groß** (`transfer:557:124`): projected gain +16.0. The move improves the projected best XI plus weighted bench by 16.0 over the configured horizon; incoming availability is 100%.
- **Tzolis → Barnes** (`transfer:557:453`): projected gain +10.9. The move improves the projected best XI plus weighted bench by 10.9 over the configured horizon; incoming availability is 100%.

## Chip shortlist

- **None** (`chip:none`) — selected: projected uplift +0.0. Preserve the first-half chips for a stronger opportunity before GW19.
- **Triple Captain** (`chip:triple_captain`): projected uplift +7.9. Adds one extra copy of Haaland's projected 7.9 points.
- **Bench Boost** (`chip:bench_boost`): projected uplift +2.2. The four substitutes project for 2.2 points in total.
- **Free Hit** (`chip:free_hit`): projected uplift +22.0. Bounded one-Gameweek legal squad search compared with the current best XI.
  - Optimized squad: Pickford, Verbruggen, Tarkowski, Davis, Hall, Thomas, Branthwaite, Schade, Groß, B.Fernandes, Cunha, Yarmoliuk, Haaland, McBurnie, Kostoulas
- **Wildcard** (`chip:wildcard`): projected uplift +42.1. Bounded permanent-squad search across the configured planning horizon.
  - Optimized squad: Leno, Raya, De Cuyper, Virgil, Guéhi, Gvardiol, Tarkowski, Barnes, Belloumi, Groß, Saka, Schade, Emersonn, Kostoulas, Haaland

## Rolling short-term plan

Combined model score over the 5-Gameweek route: **351.6**. This is a comparative rating, not a literal points forecast.

| GW | Transfers | Captain | Chip | Hit | Free transfers after | Bank | Model score | Confidence |
|---:|---|---|---|---:|---:|---:|---:|---|
| 6 | Tzolis → Schade | Haaland | None | 0 | 1 | £0.1m | 67.9 | Medium |
| 7 | van Ewijk → Dasilva | Haaland | None | 0 | 1 | £0.1m | 72.0 | Medium |
| 8 | Roll / no transfer | Haaland | None | 0 | 2 | £0.1m | 72.5 | Medium |
| 9 | Roll / no transfer | Haaland | None | 0 | 3 | £0.1m | 67.1 | Low |
| 10 | Tzolakis → Petrović | Haaland | None | 0 | 3 | £0.2m | 72.1 | Low |

### Gameweek 6 projected team

- **Starting XI:** Tzolakis, Gabriel, Gvardiol, Calafiori, Ajayi, Schade, B.Fernandes, Mbeumo, Szoboszlai, Haaland, Calvert-Lewin
- **Bench:** van Ewijk, Kusi-Asare, Hughes; reserve goalkeeper Dubravka
- **Reasoning:** Current reviewed action; later weeks are optimized from this legal state.

### Gameweek 7 projected team

- **Starting XI:** Tzolakis, Gvardiol, Gabriel, Calafiori, Dasilva, Ajayi, B.Fernandes, Mbeumo, Szoboszlai, Schade, Haaland
- **Bench:** Calvert-Lewin, Kusi-Asare, Hughes; reserve goalkeeper Dubravka
- **Reasoning:** Conditional route: the moves improve remaining-horizon player ratings by 7.1.

### Gameweek 8 projected team

- **Starting XI:** Tzolakis, Gabriel, Gvardiol, Calafiori, Dasilva, B.Fernandes, Schade, Mbeumo, Szoboszlai, Haaland, Calvert-Lewin
- **Bench:** Ajayi, Hughes, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 9 projected team

- **Starting XI:** Tzolakis, Gvardiol, Gabriel, Ajayi, Calafiori, B.Fernandes, Schade, Mbeumo, Szoboszlai, Haaland, Calvert-Lewin
- **Bench:** Dasilva, Hughes, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 10 projected team

- **Starting XI:** Petrović, Gabriel, Calafiori, Gvardiol, Dasilva, B.Fernandes, Mbeumo, Szoboszlai, Schade, Haaland, Calvert-Lewin
- **Bench:** Ajayi, Kusi-Asare, Hughes; reserve goalkeeper Dubravka
- **Reasoning:** Conditional route: the moves improve remaining-horizon player ratings by 2.3.

## Provisional long-term chip calendar

These are decision gates, not chips already applied to the short-term route. If one is activated, the route will be rebuilt from the resulting squad.

| Chip | Primary window | Backup | Target | Uplift | Confidence |
|---|---|---|---|---:|---|
| Wildcard | Unassigned | None | — | 0.0 | Low |
| Free Hit | GW17 | GW18 | — | 6.2 | Low |
| Bench Boost | GW9 | GW8 | — | 4.3 | Low |
| Triple Captain | GW7 | GW16 | Haaland | 10.0 | Medium |

### Chip-window reasoning

- **Wildcard:** No credible current window; reassess after the next deadline.
- **Free Hit:** One-Gameweek optimized squad compared with the planned route squad.
- **Bench Boost:** Projected points from the four substitutes in the route squad.
- **Triple Captain:** One extra copy of Haaland's captain projection in a home fixture against a promoted club.

## Changes since the previous saved plan

- GW6 transfer plan changed: Roll / no transfer → Tzolis → Schade.
- GW6 captain changed: B.Fernandes → Haaland.
- GW7 transfer plan changed: Tzolis → Schade, van Ewijk → Thomas → van Ewijk → Dasilva.

> Bounded rolling-horizon search using current prices and projections; future actions are provisional and recalculated every run.

## Validation

- 15-player squad and position quotas valid
- Maximum three players per club valid
- Transfer budget valid; projected bank £0.1m
- Points hit 0
- Selected reviewed engine option transfer:557:94
- Selected legal chip option chip:none
- Projection sanity bounds passed
- Mini-league risk mode balanced
- Reachable 5-Gameweek rolling route validated
- Recent forecast calibration: 3.01 points MAE and 16.7 minutes MAE across 4 Gameweeks

> Recommendation only: confirm team news and make any changes yourself in FPL.
