# Gameweek 7 recommendation

Historical Wildcard experiment before the search fixes. See
`latest_wildcard_review.md` for the current comparison, including Haaland-retaining drafts.

- **Deadline:** 2026-10-17 10:00 UTC
- **Run window:** 45m
- **Transfers:** Roll / no transfer
- **Cost / points hit:** 0
- **Captain:** Semenyo
- **Vice-captain:** Groß
- **Chip:** Wildcard
- **Confidence:** Medium
- **Analysis source:** deterministic

## Starting XI

Verbruggen, De Cuyper, Guéhi, Tarkowski, Dasilva, Semenyo, Groß, Cherki, Cunha, Palmer, João Pedro

## Bench

1. Brobbey, 2. Gabriel, 3. Barry

Reserve goalkeeper: Raya

## Explanation

Roll the transfer. No urgent availability problem clears the configured multi-fixture gain threshold, so a points-free hold is preferred. Transfers are assessed across the next 5 Gameweeks. The starting XI, bench order and captaincy are assessed separately for this Gameweek because those changes are free. Chip choice: Wildcard; estimated uplift 40.6. Risk mode: balanced.

### Confidence notes

- Captaincy is close: the top-two model margin is only 0.01 points.
- The hold policy conflicts with a shortlisted model gain of 17.9.

## Current-Gameweek projections

Expected points are model estimates; expected minutes express role uncertainty rather than guaranteed playing time.

| Player | Role | Expected minutes | Expected points |
|---|---|---:|---:|
| Semenyo | Captain | 88 | 8.75 |
| Groß | Vice-Captain | 87 | 8.68 |
| De Cuyper | Starter | 82 | 8.54 |
| Cherki | Starter | 69 | 8.07 |
| Cunha | Starter | 83 | 7.50 |
| Guéhi | Starter | 87 | 6.74 |
| Verbruggen | Starter | 86 | 6.62 |
| Palmer | Starter | 87 | 6.54 |
| Tarkowski | Starter | 87 | 6.39 |
| João Pedro | Starter | 73 | 6.31 |
| Dasilva | Starter | 85 | 6.09 |
| Brobbey | Bench | 68 | 5.62 |
| Gabriel | Bench | 88 | 4.79 |
| Barry | Bench | 83 | 4.17 |
| Raya | Reserve Goalkeeper | 87 | 4.34 |
| Gvardiol | Transfer Candidate | 74 | 6.17 |
| Dewsbury-Hall | Transfer Candidate | 87 | 5.50 |
| Schade | Transfer Candidate | 62 | 2.90 |
| Szoboszlai | Transfer Candidate | 18 | 0.26 |

## Engine shortlist

- **Roll the free transfer** (`hold`) — selected: projected gain +0.0. Preserves flexibility and avoids acting on a marginal projection.
- **Szoboszlai → Groß** (`transfer:368:124`): projected gain +17.9. The move improves the projected best XI plus weighted bench by 17.9 over the configured horizon; incoming availability is 100%. Price timing: Szoboszlai projects -93% toward a fall; that fall would cut the selling price by £0.1m. Groß projects 154% toward a rise, so waiting could add £0.1m to the buying price.
- **Szoboszlai → Dewsbury-Hall** (`transfer:368:236`): projected gain +14.1. The move improves the projected best XI plus weighted bench by 14.1 over the configured horizon; incoming availability is 100%. Price timing: Szoboszlai projects -93% toward a fall; that fall would cut the selling price by £0.1m.
- **Schade → Groß** (`transfer:94:124`): projected gain +13.1. The move improves the projected best XI plus weighted bench by 13.1 over the configured horizon; incoming availability is 100%. Price timing: Schade projects -114% toward a fall; that fall would cut the selling price by £0.1m. Groß projects 154% toward a rise, so waiting could add £0.1m to the buying price.
- **Gvardiol → De Cuyper** (`transfer:391:115`): projected gain +3.2. The move improves the projected best XI plus weighted bench by 3.2 over the configured horizon; incoming availability is 100%. Price timing: De Cuyper projects 136% toward a rise, so waiting could add £0.1m to the buying price. Market-watch candidate: De Cuyper has 869,935 net transfers in this Gameweek; that momentum does not add to the points projection.

## Chip shortlist

- **None** (`chip:none`): projected uplift +0.0. Preserve the first-half chips for a stronger opportunity before GW19.
- **Triple Captain** (`chip:triple_captain`): projected uplift +9.3. Adds one extra copy of Haaland's projected 9.3 points.
- **Bench Boost** (`chip:bench_boost`): projected uplift +3.5. The four substitutes project for 3.5 points in total.
- **Free Hit** (`chip:free_hit`): projected uplift +20.3. Bounded one-Gameweek legal squad search compared with the current best XI.
  - Optimized squad: Rushworth, Kinsky, Tarkowski, De Cuyper, Dasilva, Giles, O'Shea, Semenyo, Cunha, Palmer, Cherki, Groß, Georginio, Haaland, Brobbey
- **Wildcard** (`chip:wildcard`) — selected: projected uplift +40.6. Bounded permanent-squad search across the configured planning horizon.
  - Optimized squad: Raya, Verbruggen, Gabriel, De Cuyper, Dasilva, Guéhi, Tarkowski, Palmer, Cunha, Semenyo, Groß, Cherki, Barry, João Pedro, Brobbey

## Rolling short-term plan

Combined model score over the 5-Gameweek route: **369.8**. This is a comparative rating, not a literal points forecast.

| GW | Transfers | Captain | Chip | Hit | Free transfers after | Bank | Model score | Confidence |
|---:|---|---|---|---:|---:|---:|---:|---|
| 7 | Roll / no transfer | Semenyo | Wildcard | 0 | 1 | £0.0m | 89.0 | Medium |
| 8 | Roll / no transfer | Palmer | None | 0 | 2 | £0.0m | 71.0 | Medium |
| 9 | Roll / no transfer | Semenyo | None | 0 | 3 | £0.0m | 63.4 | Medium |
| 10 | Roll / no transfer | Gabriel | None | 0 | 4 | £0.0m | 72.9 | Low |
| 11 | Roll / no transfer | Semenyo | None | 0 | 5 | £0.0m | 73.4 | Low |

### Gameweek 7 projected team

- **Starting XI:** Verbruggen, De Cuyper, Guéhi, Tarkowski, Dasilva, Semenyo, Groß, Cherki, Cunha, Palmer, João Pedro
- **Bench:** Brobbey, Gabriel, Barry; reserve goalkeeper Raya
- **Reasoning:** Current reviewed action; later weeks are optimized from this legal state.

### Gameweek 8 projected team

- **Starting XI:** Raya, Gabriel, Guéhi, Dasilva, De Cuyper, Palmer, Semenyo, Cunha, Cherki, Groß, João Pedro
- **Bench:** Tarkowski, Brobbey, Barry; reserve goalkeeper Verbruggen
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 9 projected team

- **Starting XI:** Raya, Tarkowski, Guéhi, Gabriel, Semenyo, Palmer, Cherki, Cunha, Brobbey, João Pedro, Barry
- **Bench:** Dasilva, Groß, De Cuyper; reserve goalkeeper Verbruggen
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 10 projected team

- **Starting XI:** Raya, Gabriel, Tarkowski, Guéhi, Palmer, Semenyo, Cunha, Cherki, Groß, João Pedro, Barry
- **Bench:** De Cuyper, Dasilva, Brobbey; reserve goalkeeper Verbruggen
- **Reasoning:** Roll to preserve transfer flexibility.

### Gameweek 11 projected team

- **Starting XI:** Verbruggen, Guéhi, Gabriel, De Cuyper, Tarkowski, Semenyo, Palmer, Cherki, Groß, Cunha, João Pedro
- **Bench:** Dasilva, Barry, Brobbey; reserve goalkeeper Raya
- **Reasoning:** Roll to preserve transfer flexibility.

## Provisional long-term chip calendar

These are decision gates, not chips already applied to the short-term route. If one is activated, the route will be rebuilt from the resulting squad.

| Chip | Primary window | Backup | Target | Uplift | Confidence |
|---|---|---|---|---:|---|
| Wildcard | GW7 | None | — | 40.6 | High |
| Free Hit | GW18 | GW17 | — | 6.8 | Low |
| Bench Boost | GW10 | GW11 | — | 16.0 | Medium |
| Triple Captain | GW16 | GW19 | Semenyo | 6.9 | Low |

### Chip-window reasoning

- **Wildcard:** Permanent optimized squad across the next 5 Gameweeks.
- **Free Hit:** One-Gameweek optimized squad compared with the planned route squad.
- **Bench Boost:** Projected points from the four substitutes in the route squad.
- **Triple Captain:** One extra copy of Semenyo's captain projection in a home fixture against a promoted club.

## Changes since the previous saved plan

- Advanced the rolling plan from GW6 to GW7.
- GW7 transfer plan changed: Tzolis → Schade, van Ewijk → Thomas → Roll / no transfer.
- GW7 captain changed: Haaland → Semenyo.
- GW8 captain changed: Haaland → Palmer.
- GW9 captain changed: Haaland → Semenyo.
- GW10 transfer plan changed: Tzolakis → Petrović → Roll / no transfer.
- GW10 captain changed: Haaland → Gabriel.
- Wildcard target changed: Unassigned → GW7.
- Free Hit target changed: GW17 → GW18.
- Bench Boost target changed: GW9 → GW10.

> Bounded rolling-horizon search using current prices and projections; future actions are provisional and recalculated every run.

## Validation

- 15-player squad and position quotas valid
- Maximum three players per club valid
- Transfer budget valid; projected bank £0.0m
- Points hit 0
- Selected reviewed engine option hold
- Selected legal chip option chip:wildcard
- Projection sanity bounds passed
- Mini-league risk mode balanced
- Reachable 5-Gameweek rolling route validated
- Recent forecast calibration: 2.99 points MAE and 18.2 minutes MAE across 5 Gameweeks

> Recommendation only: confirm team news and make any changes yourself in FPL.
