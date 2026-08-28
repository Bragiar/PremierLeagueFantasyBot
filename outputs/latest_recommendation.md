# Gameweek 2 recommendation

- **Deadline:** 2026-08-28 17:30 UTC
- **Run window:** 3h
- **Transfers:** Roll / no transfer
- **Cost / points hit:** 0
- **Captain:** João Pedro
- **Vice-captain:** Haaland
- **Chip:** None — save the chip
- **Confidence:** High
- **Analysis source:** deterministic

## Starting XI

Verbruggen, Calafiori, Gabriel, Shaw, van Ewijk, Szoboszlai, B.Fernandes, Mbeumo, Tzolis, João Pedro, Haaland

## Bench

1. Diop, 2. Kusi-Asare, 3. Hughes

Reserve goalkeeper: Dubravka

## Explanation

Roll the transfer. No urgent availability problem clears the configured multi-fixture gain threshold, so a points-free hold is preferred. Transfers are assessed across the next 5 Gameweeks. The starting XI, bench order and captaincy are assessed separately for this Gameweek because those changes are free. Chip choice: None; estimated uplift 0.0.

## Engine shortlist

- **Roll the free transfer** (`hold`) — selected: projected gain +0.0. Preserves flexibility and avoids acting on a marginal projection.
- **Shaw → Justin** (`transfer:423:332`): projected gain +14.2. Engine scores Justin 14.2 points above Shaw over the configured horizon; incoming availability is 100%.
- **Mbeumo → Gakpo** (`transfer:427:367`): projected gain +13.4. Engine scores Gakpo 13.4 points above Mbeumo over the configured horizon; incoming availability is 100%.
- **Mbeumo → Dewsbury-Hall** (`transfer:427:236`): projected gain +11.8. Engine scores Dewsbury-Hall 11.8 points above Mbeumo over the configured horizon; incoming availability is 100%.

## Chip shortlist

- **None** (`chip:none`) — selected: projected uplift +0.0. Preserve the first-half chips for a stronger opportunity before GW19.
- **Triple Captain** (`chip:triple_captain`): projected uplift +10.4. Adds one extra copy of João Pedro's projected 10.4 points.
- **Bench Boost** (`chip:bench_boost`): projected uplift +8.3. The four substitutes project for 8.3 points in total.
- **Free Hit** (`chip:free_hit`): projected uplift +21.0. Bounded one-Gameweek legal squad search compared with the current best XI.
  - Optimized squad: Tzolakis, Dovin, Justin, Gvardiol, Bijol, Thomas, Guéhi, Gakpo, Xhaka, Palmer, Dewsbury-Hall, Szoboszlai, Obi, Mheuka, João Pedro
- **Wildcard** (`chip:wildcard`): projected uplift +86.5. Bounded permanent-squad search across the configured planning horizon.
  - Optimized squad: Trafford, Raya, Gvardiol, White, Guéhi, Bijol, Calafiori, Ndiaye, Szoboszlai, Palmer, Dewsbury-Hall, Gakpo, Emersonn, Barry, João Pedro

## Rolling short-term plan

Combined model score over the 5-Gameweek route: **491.7**. This is a comparative rating, not a literal points forecast.

| GW | Transfers | Captain | Chip | Hit | Free transfers after | Bank | Model score | Confidence |
|---:|---|---|---|---:|---:|---:|---:|---|
| 2 | Roll / no transfer | João Pedro | None | 0 | 2 | £0.0m | 85.4 | High |
| 3 | Hughes → George Hemmings | Haaland | None | 0 | 2 | £0.0m | 100.8 | Medium |
| 4 | Roll / no transfer | Haaland | None | 0 | 3 | £0.0m | 100.6 | Medium |
| 5 | Roll / no transfer | Haaland | None | 0 | 4 | £0.0m | 102.2 | Low |
| 6 | Roll / no transfer | Haaland | None | 0 | 5 | £0.0m | 102.6 | Low |

### Gameweek 2 projected team

- **Starting XI:** Verbruggen, Calafiori, Gabriel, Shaw, van Ewijk, Szoboszlai, B.Fernandes, Mbeumo, Tzolis, João Pedro, Haaland
- **Bench:** Diop, Kusi-Asare, Hughes; reserve goalkeeper Dubravka
- **Reasoning:** Current reviewed action; later weeks are optimized from this legal state.

### Gameweek 3 projected team

- **Starting XI:** Verbruggen, Gabriel, Calafiori, Shaw, B.Fernandes, Szoboszlai, Mbeumo, Tzolis, George Hemmings, Haaland, João Pedro
- **Bench:** Diop, Kusi-Asare, van Ewijk; reserve goalkeeper Dubravka
- **Reasoning:** Conditional route: the moves improve remaining-horizon player ratings by 5.9.

### Gameweek 4 projected team

- **Starting XI:** Verbruggen, Gabriel, Calafiori, van Ewijk, Diop, B.Fernandes, Szoboszlai, Tzolis, Mbeumo, Haaland, João Pedro
- **Bench:** George Hemmings, Shaw, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 5 projected team

- **Starting XI:** Verbruggen, Gabriel, Calafiori, Shaw, van Ewijk, B.Fernandes, Mbeumo, Szoboszlai, Tzolis, Haaland, João Pedro
- **Bench:** Diop, George Hemmings, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 6 projected team

- **Starting XI:** Verbruggen, Gabriel, Calafiori, van Ewijk, Diop, B.Fernandes, Mbeumo, Tzolis, Szoboszlai, Haaland, João Pedro
- **Bench:** Shaw, George Hemmings, Kusi-Asare; reserve goalkeeper Dubravka
- **Reasoning:** Roll to preserve transfer flexibility.

## Provisional long-term chip calendar

These are decision gates, not chips already applied to the short-term route. If one is activated, the route will be rebuilt from the resulting squad.

| Chip | Primary window | Backup | Target | Uplift | Confidence |
|---|---|---|---|---:|---|
| Wildcard | GW3 | GW4 | — | 27.9 | Medium |
| Free Hit | GW9 | GW11 | — | 7.0 | Low |
| Bench Boost | GW6 | GW15 | — | 16.4 | Medium |
| Triple Captain | GW16 | GW7 | Haaland | 13.9 | Low |

### Chip-window reasoning

- **Wildcard:** Permanent optimized squad across the next 5 Gameweeks.
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
- Reachable 5-Gameweek rolling route validated

> Recommendation only: confirm team news and make any changes yourself in FPL.
