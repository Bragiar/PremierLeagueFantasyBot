# Gameweek 3 recommendation

- **Deadline:** 2026-09-04 17:30 UTC
- **Run window:** manual
- **Transfers:** Shaw → Ajayi (£4.5m → £4.0m)
- **Cost / points hit:** 0
- **Captain:** Ajayi
- **Vice-captain:** Haaland
- **Chip:** None — save the chip
- **Confidence:** Low
- **Analysis source:** deterministic

## Starting XI

Verbruggen, Ajayi, Calafiori, Gabriel, Szoboszlai, Tzolis, B.Fernandes, Mbeumo, Haaland, João Pedro, Kusi-Asare

## Bench

1. Hughes, 2. Diop, 3. van Ewijk

Reserve goalkeeper: Dubravka

## Explanation

Use one free transfer: Shaw to Ajayi. The move remains within budget with £0.5m left and passes all squad rules. Transfers are assessed across the next 5 Gameweeks. The starting XI, bench order and captaincy are assessed separately for this Gameweek because those changes are free. Chip choice: None; estimated uplift 0.0. Risk mode: balanced.

### Confidence notes

- Only 2 completed Gameweeks of current-season evidence.
- Expected-minutes uncertainty: Verbruggen, Tzolis, Kusi-Asare.
- Captaincy is close: the top-two model margin is only 0.20 points.

## Current-Gameweek projections

Expected points are model estimates; expected minutes express role uncertainty rather than guaranteed playing time.

| Player | Role | Expected minutes | Expected points |
|---|---|---:|---:|
| Ajayi | Captain | 65 | 10.24 |
| Haaland | Vice-Captain | 85 | 9.32 |
| Szoboszlai | Starter | 76 | 7.70 |
| Verbruggen | Starter | 50 | 4.35 |
| Calafiori | Starter | 65 | 4.25 |
| João Pedro | Starter | 65 | 4.23 |
| Tzolis | Starter | 52 | 2.39 |
| Gabriel | Starter | 60 | 1.99 |
| B.Fernandes | Starter | 64 | 1.46 |
| Mbeumo | Starter | 59 | 1.39 |
| Kusi-Asare | Starter | 17 | 0.78 |
| Hughes | Bench | 17 | 0.78 |
| Diop | Bench | 48 | 0.13 |
| van Ewijk | Bench | 65 | 0.00 |
| Dubravka | Reserve Goalkeeper | 17 | 0.63 |
| M.Sangaré | Transfer Candidate | 65 | 8.55 |
| Kayode | Transfer Candidate | 65 | 8.08 |
| Janelt | Transfer Candidate | 65 | 6.35 |
| Shaw | Transfer Candidate | 49 | 0.62 |

## Engine shortlist

- **Roll the free transfer** (`hold`): projected gain +0.0. Preserves flexibility and avoids acting on a marginal projection.
- **Tzolis → M.Sangaré** (`transfer:557:565`): projected gain +19.9. Engine scores M.Sangaré 19.9 points above Tzolis over the configured horizon; incoming availability is 100%.
- **Gabriel → Kayode** (`transfer:4:88`): projected gain +19.5. Engine scores Kayode 19.5 points above Gabriel over the configured horizon; incoming availability is 100%.
- **Mbeumo → Janelt** (`transfer:427:98`): projected gain +19.5. Engine scores Janelt 19.5 points above Mbeumo over the configured horizon; incoming availability is 100%.
- **Shaw → Ajayi** (`transfer:423:279`) — selected: projected gain +48.2. The deterministic safety policy selected this legal move for an availability risk; projected gain is 48.2.

## Chip shortlist

- **None** (`chip:none`) — selected: projected uplift +0.0. Preserve the first-half chips for a stronger opportunity before GW19.
- **Triple Captain** (`chip:triple_captain`): projected uplift +10.2. Adds one extra copy of Ajayi's projected 10.2 points.
- **Bench Boost** (`chip:bench_boost`): projected uplift +1.5. The four substitutes project for 1.5 points in total.
- **Free Hit** (`chip:free_hit`): projected uplift +59.0. Bounded one-Gameweek legal squad search compared with the current best XI.
  - Optimized squad: Tzolakis, Verbruggen, Ajayi, Egan, Tarkowski, De Cuyper, Gvardiol, Cherki, Janelt, M.Sangaré, Elanga, Gakpo, Haaland, Simms, Barry
- **Wildcard** (`chip:wildcard`): projected uplift +272.2. Bounded permanent-squad search across the configured planning horizon.
  - Optimized squad: Tzolakis, Pickford, Ajayi, Egan, Hall, De Cuyper, Tarkowski, Cherki, Scott, Gibbs-White, Elanga, Gakpo, Haaland, João Pedro, Wissa

## Rolling short-term plan

Combined model score over the 5-Gameweek route: **320.3**. This is a comparative rating, not a literal points forecast.

| GW | Transfers | Captain | Chip | Hit | Free transfers after | Bank | Model score | Confidence |
|---:|---|---|---|---:|---:|---:|---:|---|
| 3 | Shaw → Ajayi | Ajayi | None | 0 | 2 | £0.5m | 58.3 | Low |
| 4 | Hughes → Armstrong | Haaland | None | 0 | 2 | £0.0m | 63.0 | Medium |
| 5 | Verbruggen → Tzolakis | Haaland | None | 0 | 2 | £0.0m | 68.0 | Medium |
| 6 | Roll / no transfer | Haaland | None | 0 | 3 | £0.0m | 65.7 | Low |
| 7 | Roll / no transfer | Haaland | None | 0 | 4 | £0.0m | 65.4 | Low |

### Gameweek 3 projected team

- **Starting XI:** Verbruggen, Ajayi, Calafiori, Gabriel, Szoboszlai, Tzolis, B.Fernandes, Mbeumo, Haaland, João Pedro, Kusi-Asare
- **Bench:** Hughes, Diop, van Ewijk; reserve goalkeeper Dubravka
- **Reasoning:** Current reviewed action; later weeks are optimized from this legal state.

### Gameweek 4 projected team

- **Starting XI:** Verbruggen, Gabriel, Calafiori, van Ewijk, Szoboszlai, B.Fernandes, Tzolis, Mbeumo, Armstrong, Haaland, João Pedro
- **Bench:** Ajayi, Diop, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Conditional route: the moves improve remaining-horizon player ratings by 11.4.

### Gameweek 5 projected team

- **Starting XI:** Tzolakis, Gabriel, Calafiori, Ajayi, B.Fernandes, Szoboszlai, Mbeumo, Armstrong, Tzolis, Haaland, João Pedro
- **Bench:** van Ewijk, Diop, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Conditional route: the moves improve remaining-horizon player ratings by 4.0.

### Gameweek 6 projected team

- **Starting XI:** Tzolakis, Gabriel, Calafiori, van Ewijk, B.Fernandes, Mbeumo, Tzolis, Armstrong, Szoboszlai, Haaland, João Pedro
- **Bench:** Ajayi, Diop, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 7 projected team

- **Starting XI:** Tzolakis, Gabriel, Calafiori, Ajayi, van Ewijk, B.Fernandes, Mbeumo, Szoboszlai, Tzolis, Haaland, João Pedro
- **Bench:** Armstrong, Kusi-Asare, Diop; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

## Provisional long-term chip calendar

These are decision gates, not chips already applied to the short-term route. If one is activated, the route will be rebuilt from the resulting squad.

| Chip | Primary window | Backup | Target | Uplift | Confidence |
|---|---|---|---|---:|---|
| Wildcard | Unassigned | None | — | 0.0 | Low |
| Free Hit | GW17 | GW18 | — | 9.3 | Low |
| Bench Boost | GW9 | GW6 | — | 7.0 | Low |
| Triple Captain | GW7 | GW16 | Haaland | 9.8 | Medium |

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
- Transfer budget valid; projected bank £0.5m
- Points hit 0
- Selected reviewed engine option transfer:423:279
- Selected legal chip option chip:none
- Projection sanity bounds passed
- Mini-league risk mode balanced
- Reachable 5-Gameweek rolling route validated

> Recommendation only: confirm team news and make any changes yourself in FPL.
