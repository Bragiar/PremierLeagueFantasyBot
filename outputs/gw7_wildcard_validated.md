# Gameweek 7 recommendation

- **Deadline:** 2026-10-17 10:00 UTC
- **Run window:** 45m
- **Transfers:** Wildcard squad rebuild
- **Cost / points hit:** 0
- **Captain:** Haaland
- **Vice-captain:** Semenyo
- **Chip:** Wildcard
- **Confidence:** Medium
- **Analysis source:** deterministic

## Starting XI

Verbruggen, De Cuyper, Guéhi, Tarkowski, Dasilva, Semenyo, Groß, Rogers, McGinn, Haaland, João Pedro

## Bench

1. Calafiori, 2. Tonali, 3. Barry

Reserve goalkeeper: Trafford

## Explanation

Rebuild the squad with Wildcard; transfers cost no points. The legal squad leaves £0.3m in the bank. Transfers are assessed across the next 5 Gameweeks. The starting XI, bench order and captaincy are assessed separately for this Gameweek because those changes are free. Chip choice: Wildcard; estimated uplift 51.7. Risk mode: balanced.

### Confidence notes

- The last three settled forecast XIs overpredicted by at least 10 points each (average 30.5); treat optimizer gains cautiously. These are forecast lineups, not confirmed user results.
- Captaincy is close: the top-two model margin is only 0.74 points.
- Wildcard comparison: WC GW7; unrestricted leads the selected no-chip route by +36.2 model score; later chip value is unpriced. See outputs/latest_wildcard_review.md before choosing a chip.

## Current-Gameweek projections

Expected points are model estimates; expected minutes express role uncertainty rather than guaranteed playing time.

| Player | Role | Expected minutes | Expected points |
|---|---|---:|---:|
| Haaland | Captain | 88 | 9.26 |
| Semenyo | Vice-Captain | 88 | 8.75 |
| Groß | Starter | 87 | 8.68 |
| De Cuyper | Starter | 82 | 8.54 |
| Guéhi | Starter | 87 | 6.74 |
| Verbruggen | Starter | 86 | 6.62 |
| Tarkowski | Starter | 87 | 6.39 |
| João Pedro | Starter | 73 | 6.31 |
| Rogers | Starter | 86 | 6.24 |
| Dasilva | Starter | 85 | 6.09 |
| McGinn | Starter | 85 | 5.80 |
| Calafiori | Bench | 83 | 5.67 |
| Tonali | Bench | 84 | 5.37 |
| Barry | Bench | 83 | 4.17 |
| Trafford | Reserve Goalkeeper | 86 | 4.18 |
| Gvardiol | Transfer Candidate | 74 | 6.17 |
| Dewsbury-Hall | Transfer Candidate | 87 | 5.50 |
| Schade | Transfer Candidate | 62 | 2.90 |
| Szoboszlai | Transfer Candidate | 18 | 0.26 |

## Engine shortlist

- **Roll the free transfer** (`hold`) — selected: projected gain +0.0. Preserves flexibility and avoids acting on a marginal projection.
- **Szoboszlai → Groß** (`transfer:368:124`): projected gain +17.9. The move improves the projected best XI plus weighted bench by 17.9 over the configured horizon; incoming availability is 100%. Price timing: Szoboszlai projects -102% toward a fall; that fall would cut the selling price by £0.1m. Groß projects 167% toward a rise, so waiting could add £0.1m to the buying price.
- **Szoboszlai → Dewsbury-Hall** (`transfer:368:236`): projected gain +14.1. The move improves the projected best XI plus weighted bench by 14.1 over the configured horizon; incoming availability is 100%. Price timing: Szoboszlai projects -102% toward a fall; that fall would cut the selling price by £0.1m.
- **Schade → Groß** (`transfer:94:124`): projected gain +13.1. The move improves the projected best XI plus weighted bench by 13.1 over the configured horizon; incoming availability is 100%. Price timing: Schade projects -123% toward a fall; that fall would cut the selling price by £0.1m. Groß projects 167% toward a rise, so waiting could add £0.1m to the buying price.
- **Gvardiol → De Cuyper** (`transfer:391:115`): projected gain +3.2. The move improves the projected best XI plus weighted bench by 3.2 over the configured horizon; incoming availability is 100%. Price timing: De Cuyper projects 147% toward a rise, so waiting could add £0.1m to the buying price. Market-watch candidate: De Cuyper has 883,345 net transfers in this Gameweek; that momentum does not add to the points projection.

## Chip shortlist

- **None** (`chip:none`): projected uplift +0.0. Preserve the first-half chips for a stronger opportunity before GW19.
- **Triple Captain** (`chip:triple_captain`): projected uplift +9.3. Adds one extra copy of Haaland's projected 9.3 points.
- **Bench Boost** (`chip:bench_boost`): projected uplift +3.5. The four substitutes project for 3.5 points in total.
- **Free Hit** (`chip:free_hit`): projected uplift +20.4. Bounded one-Gameweek legal squad search compared with the current best XI.
  - Optimized squad: Haaland, Rushworth, Kinsky, Tarkowski, De Cuyper, Dasilva, Giles, O'Shea, Semenyo, Cunha, Palmer, Cherki, Groß, Kostoulas, Delap
- **Wildcard** (`chip:wildcard`) — selected: projected uplift +51.7. Bounded permanent-squad search across the configured planning horizon.
  - Optimized squad: Haaland, Trafford, Verbruggen, Calafiori, De Cuyper, Dasilva, Guéhi, Tarkowski, Semenyo, McGinn, Rogers, Groß, Tonali, Barry, João Pedro

## Rolling short-term plan

Combined model score over the 5-Gameweek route: **380.7**. This is a comparative rating, not a literal points forecast.

| GW | Transfers | Captain | Chip | Hit | Free transfers after | Bank | Model score | Confidence |
|---:|---|---|---|---:|---:|---:|---:|---|
| 7 | Wildcard squad rebuild | Haaland | Wildcard | 0 | 1 | £0.3m | 88.7 | Medium |
| 8 | Roll / no transfer | Haaland | None | 0 | 2 | £0.3m | 71.3 | Medium |
| 9 | Roll / no transfer | Haaland | None | 0 | 3 | £0.3m | 68.1 | Medium |
| 10 | Roll / no transfer | Haaland | None | 0 | 4 | £0.3m | 75.0 | Low |
| 11 | Roll / no transfer | Haaland | None | 0 | 5 | £0.3m | 77.6 | Low |

### Gameweek 7 projected team

- **Starting XI:** Verbruggen, De Cuyper, Guéhi, Tarkowski, Dasilva, Semenyo, Groß, Rogers, McGinn, Haaland, João Pedro
- **Bench:** Calafiori, Tonali, Barry; reserve goalkeeper Trafford
- **Reasoning:** Current reviewed action; later weeks are optimized from this legal state.

### Gameweek 8 projected team

- **Starting XI:** Trafford, Guéhi, Calafiori, Dasilva, De Cuyper, Tarkowski, Rogers, Semenyo, Groß, Haaland, João Pedro
- **Bench:** McGinn, Tonali, Barry; reserve goalkeeper Verbruggen
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 9 projected team

- **Starting XI:** Trafford, Tarkowski, Guéhi, Calafiori, Semenyo, McGinn, Rogers, Tonali, Haaland, João Pedro, Barry
- **Bench:** Dasilva, Groß, De Cuyper; reserve goalkeeper Verbruggen
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 10 projected team

- **Starting XI:** Trafford, Tarkowski, Calafiori, Guéhi, De Cuyper, Semenyo, Rogers, Groß, Haaland, João Pedro, Barry
- **Bench:** Tonali, Dasilva, McGinn; reserve goalkeeper Verbruggen
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 11 projected team

- **Starting XI:** Verbruggen, Guéhi, De Cuyper, Tarkowski, Calafiori, Semenyo, Groß, Rogers, Tonali, Haaland, João Pedro
- **Bench:** Dasilva, Barry, McGinn; reserve goalkeeper Trafford
- **Reasoning:** Roll to preserve transfer flexibility.

## Provisional long-term chip calendar

These are decision gates, not chips already applied to the short-term route. If one is activated, the route will be rebuilt from the resulting squad.

| Chip | Primary window | Backup | Target | Uplift | Confidence |
|---|---|---|---|---:|---|
| Wildcard | GW7 | None | — | 51.7 | High |
| Free Hit | GW18 | GW17 | — | 6.1 | Low |
| Bench Boost | GW10 | GW11 | — | 14.8 | Medium |
| Triple Captain | GW16 | GW19 | Haaland | 10.0 | Low |

### Chip-window reasoning

- **Wildcard:** Permanent optimized squad across the next 5 Gameweeks.
- **Free Hit:** One-Gameweek optimized squad compared with the planned route squad.
- **Bench Boost:** Projected points from the four substitutes in the route squad.
- **Triple Captain:** One extra copy of Haaland's captain projection in a home fixture against a promoted club.

## Changes since the previous saved plan

- GW7 transfer plan changed: Szoboszlai → Groß → Wildcard squad rebuild.
- GW8 transfer plan changed: Ajayi → Dasilva → Roll / no transfer.
- GW9 transfer plan changed: Schade → Dewsbury-Hall → Roll / no transfer.
- GW10 transfer plan changed: Dubravka → Verbruggen → Roll / no transfer.
- Wildcard target changed: Unassigned → GW7.
- Bench Boost target changed: GW11 → GW10.

> Bounded rolling-horizon search using current prices and projections; future actions are provisional and recalculated every run.

## Validation

- 15-player squad and position quotas valid
- Maximum three players per club valid
- Transfer budget valid; projected bank £0.3m
- Points hit 0
- Selected reviewed engine option hold
- Selected legal chip option chip:wildcard
- Projection sanity bounds passed
- Mini-league risk mode balanced
- Reachable 5-Gameweek rolling route validated
- Recent forecast calibration: 2.99 points MAE and 18.2 minutes MAE across 5 Gameweeks

> Recommendation only: confirm team news and make any changes yourself in FPL.
