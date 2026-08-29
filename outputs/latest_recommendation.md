# Gameweek 2 recommendation

- **Deadline:** 2026-08-28 17:30 UTC
- **Run window:** manual
- **Transfers:** Roll / no transfer
- **Cost / points hit:** 0
- **Captain:** B.Fernandes
- **Vice-captain:** João Pedro
- **Chip:** None — save the chip
- **Confidence:** Medium
- **Analysis source:** deterministic

## Starting XI

Verbruggen, Gabriel, Shaw, Calafiori, van Ewijk, B.Fernandes, Mbeumo, Szoboszlai, Tzolis, João Pedro, Haaland

## Bench

1. Diop, 2. Kusi-Asare, 3. Hughes

Reserve goalkeeper: Dubravka

## Explanation

Roll the transfer. No urgent availability problem clears the configured multi-fixture gain threshold, so a points-free hold is preferred. Transfers are assessed across the next 5 Gameweeks. The starting XI, bench order and captaincy are assessed separately for this Gameweek because those changes are free. Chip choice: None; estimated uplift 0.0. Risk mode: balanced.

### Confidence notes

- Only 1 completed Gameweek of current-season evidence.
- Captaincy is close: the top-two model margin is only 0.58 points.
- The hold policy conflicts with a shortlisted model gain of 7.7.

## Current-Gameweek projections

Expected points are model estimates; expected minutes express role uncertainty rather than guaranteed playing time.

| Player | Role | Expected minutes | Expected points |
|---|---|---:|---:|
| B.Fernandes | Captain | 80 | 5.40 |
| João Pedro | Vice-Captain | 77 | 4.71 |
| Haaland | Starter | 83 | 4.47 |
| Mbeumo | Starter | 73 | 4.24 |
| Szoboszlai | Starter | 71 | 3.64 |
| Gabriel | Starter | 74 | 3.61 |
| Shaw | Starter | 60 | 2.87 |
| Calafiori | Starter | 66 | 2.58 |
| van Ewijk | Starter | 57 | 2.20 |
| Tzolis | Starter | 64 | 2.01 |
| Verbruggen | Starter | 60 | 1.60 |
| Diop | Bench | 58 | 0.32 |
| Kusi-Asare | Bench | 20 | 0.23 |
| Hughes | Bench | 20 | 0.00 |
| Dubravka | Reserve Goalkeeper | 20 | 0.67 |
| Slater | Transfer Candidate | 55 | 2.75 |
| Crooks | Transfer Candidate | 55 | 2.29 |
| George Hemmings | Transfer Candidate | 55 | 0.28 |

## Engine shortlist

- **Roll the free transfer** (`hold`) — selected: projected gain +0.0. Preserves flexibility and avoids acting on a marginal projection.
- **Hughes → Slater** (`transfer:212:290`): projected gain +7.7. Engine scores Slater 7.7 points above Hughes over the configured horizon; incoming availability is 100%.
- **Hughes → Crooks** (`transfer:212:289`): projected gain +5.3. Engine scores Crooks 5.3 points above Hughes over the configured horizon; incoming availability is 100%.
- **Hughes → George Hemmings** (`transfer:212:51`): projected gain +5.1. Engine scores George Hemmings 5.1 points above Hughes over the configured horizon; incoming availability is 100%.

## Chip shortlist

- **None** (`chip:none`) — selected: projected uplift +0.0. Preserve the first-half chips for a stronger opportunity before GW19.
- **Triple Captain** (`chip:triple_captain`): projected uplift +5.4. Adds one extra copy of B.Fernandes's projected 5.4 points.
- **Bench Boost** (`chip:bench_boost`): projected uplift +1.2. The four substitutes project for 1.2 points in total.
- **Free Hit** (`chip:free_hit`): projected uplift +10.6. Bounded one-Gameweek legal squad search compared with the current best XI.
  - Optimized squad: Pickford, Kinsky, Gvardiol, Senesi, Guéhi, Lacroix, Amenda, Cunha, Mbeumo, Palmer, B.Fernandes, Xhaka, McBurnie, João Pedro, Thomas-Asante
- **Wildcard** (`chip:wildcard`): projected uplift +43.0. Bounded permanent-squad search across the configured planning horizon.
  - Optimized squad: Pickford, Raya, Gabriel, Tarkowski, Gvardiol, Calafiori, Guéhi, Elanga, Szoboszlai, Rogers, Gakpo, Palmer, Wissa, Barry, João Pedro

## Rolling short-term plan

Combined model score over the 5-Gameweek route: **292.1**. This is a comparative rating, not a literal points forecast.

| GW | Transfers | Captain | Chip | Hit | Free transfers after | Bank | Model score | Confidence |
|---:|---|---|---|---:|---:|---:|---:|---|
| 2 | Roll / no transfer | B.Fernandes | None | 0 | 2 | £0.0m | 42.7 | Medium |
| 3 | Roll / no transfer | Haaland | None | 0 | 3 | £0.0m | 60.3 | Medium |
| 4 | Roll / no transfer | Haaland | None | 0 | 4 | £0.0m | 61.8 | Medium |
| 5 | Roll / no transfer | Haaland | None | 0 | 5 | £0.0m | 63.4 | Low |
| 6 | Roll / no transfer | Haaland | None | 0 | 5 | £0.0m | 63.9 | Low |

### Gameweek 2 projected team

- **Starting XI:** Verbruggen, Gabriel, Shaw, Calafiori, van Ewijk, B.Fernandes, Mbeumo, Szoboszlai, Tzolis, João Pedro, Haaland
- **Bench:** Diop, Kusi-Asare, Hughes; reserve goalkeeper Dubravka
- **Reasoning:** Current reviewed action; later weeks are optimized from this legal state.

### Gameweek 3 projected team

- **Starting XI:** Verbruggen, Gabriel, Calafiori, Shaw, Diop, B.Fernandes, Szoboszlai, Mbeumo, Tzolis, Haaland, João Pedro
- **Bench:** Hughes, Kusi-Asare, van Ewijk; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 4 projected team

- **Starting XI:** Verbruggen, Gabriel, Calafiori, van Ewijk, Diop, B.Fernandes, Szoboszlai, Tzolis, Mbeumo, Haaland, João Pedro
- **Bench:** Shaw, Hughes, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 5 projected team

- **Starting XI:** Verbruggen, Gabriel, Calafiori, Shaw, Diop, B.Fernandes, Mbeumo, Szoboszlai, Tzolis, Haaland, João Pedro
- **Bench:** van Ewijk, Hughes, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 6 projected team

- **Starting XI:** Verbruggen, Gabriel, Calafiori, Diop, van Ewijk, B.Fernandes, Tzolis, Mbeumo, Szoboszlai, Haaland, João Pedro
- **Bench:** Shaw, Kusi-Asare, Hughes; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

## Provisional long-term chip calendar

These are decision gates, not chips already applied to the short-term route. If one is activated, the route will be rebuilt from the resulting squad.

| Chip | Primary window | Backup | Target | Uplift | Confidence |
|---|---|---|---|---:|---|
| Wildcard | Unassigned | None | — | 0.0 | Low |
| Free Hit | GW17 | GW18 | — | 9.0 | Low |
| Bench Boost | GW13 | GW6 | — | 5.5 | Low |
| Triple Captain | GW7 | GW16 | Haaland | 9.5 | Low |

### Chip-window reasoning

- **Wildcard:** No credible current window; reassess after the next deadline.
- **Free Hit:** One-Gameweek optimized squad compared with the planned route squad.
- **Bench Boost:** Projected points from the four substitutes in the route squad.
- **Triple Captain:** One extra copy of Haaland's captain projection in a home fixture against a promoted club.

## Changes since the previous saved plan

- GW2 captain changed: João Pedro → B.Fernandes.
- GW3 transfer plan changed: Hughes → George Hemmings → Roll / no transfer.
- Wildcard target changed: GW3 → Unassigned.
- Free Hit target changed: GW9 → GW17.
- Bench Boost target changed: GW6 → GW13.
- Triple Captain target changed: GW16 → GW7.

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

> Recommendation only: confirm team news and make any changes yourself in FPL.
