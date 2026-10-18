# GW7 in-app review — 17 October 2026

Historical review before the Python search fixes. Its no-Haaland Wildcard assessment
is superseded by `strategy_audit_2026-10-17.md` and `latest_wildcard_review.md`.

Squad reconciled against user screenshot: Schade replaces Tzolis; Bruno captain, Haaland vice. User confirms 1 FT and £0.1m bank. Public transfer ledger confirms Schade purchased for £6.2m in GW6. Other purchase prices retained from previous record. Squad inputs reflect actual holdings, not proposed transfers.

## Final reviewed decision

Preferred transfer option: `transfer:368:124` (Szoboszlai → Groß). Preferred chip: `chip:none`. No hit; projected £0.8m bank. Haaland captain, Groß vice. Reviewer confidence: Medium, despite engine High. Python dry-run completed and validated squad quotas, club limits, budget and rolling route. No OpenAI API calls or Telegram delivery requested or used.

XI: Tzolakis; Gvardiol, Calafiori, Gabriel, Ajayi, van Ewijk; Groß, Mbeumo, B.Fernandes, Schade; Haaland. Bench: Calvert-Lewin, Kusi-Asare, Hughes; reserve GK Dubravka. Van Ewijk versus Calvert-Lewin is only 3.12 versus 2.82 model points and not a strong distinction. Schade is a fitness risk at 62 expected minutes; Gvardiol 74 and Haaland 88 also need rotation caution. Calvert-Lewin offers the meaningful first substitute; other reserves remain weak.

## Evidence and judgment

Liverpool says Szoboszlai could return, but is unconfirmed, after missing the previous league and European games; rotation is planned. Do not describe him as definitively ruled out. Brentford says Schade has been on the grass but his availability remains unresolved. This supports prioritising the engine's Szoboszlai sale, without treating Schade as safe. The Scout selects Groß and captains Haaland. City explicitly raises Haaland workload/rest concerns, although he is in the squad: ordinary captaincy remains reasonable, Triple Captain less attractive.

Sources:
- https://lfcbeta.liverpoolfc.com/news/brentford-v-liverpool-team-news-premier-league
- https://www.brentfordfc.com/en/news/first-team-news-brentford-v-liverpool-premier-league-kevin-schade-jannik-schuster
- https://www.premierleague.com/en/news/4737338/scout-selection-best-fantasy-team-for-gameweek-7
- https://beta.mancity.com/news/mens/maresca-written-ipswich-preview-63927753
- https://www.premierleague.com/en/news/4362085
- https://www.premierleague.com/en/news/4679879/whats-happening-with-fpl-chips-in-202627
- https://www.fantasyfootballpundit.com/fantasy-premier-league-team-news/

Predicted lineups are opinion: Fantasy Football Pundit includes van Ewijk at 90% to start. Neither that nor the engine's expected minutes guarantees a start.

## Wildcard assessment

A Wildcard is a legitimate option given two flagged midfielders and weak reserves. The default no-chip outcome is enforced by save_chips_by_default=true and allow_exceptional_early_chip=false before expiry pressure; it is not evidence the optimizer found waiting superior. The displayed Wildcard uplift of 40.6 is a squad-objective comparison against the proposed squad, not a 40.6-point advantage over a rolling transfer route.

A non-recording preview of the exact shortlisted chip:wildcard draft passed legality and budget checks, with £0.0m remaining. Draft: Raya, Verbruggen; Gabriel, De Cuyper, Dasilva, Guéhi, Tarkowski; Palmer, Cunha, Semenyo, Groß, Cherki; Barry, João Pedro, Brobbey. It removes Haaland, Bruno and Mbeumo and captains Semenyo this week. Its rolling comparative score is 369.77 versus 350.33 for the finalized transfer route (+19.44); scores are not literal point forecasts. The overhaul improves depth but entails a major captaincy/structure change and some uncertain roles (Cherki 69 minutes, João Pedro 73, Brobbey 68). There is insufficient high-confidence support from two recent sources for selecting this exact no-Haaland draft over the engine default. Keep chip:none. Comparison saved separately in gw7_wildcard_comparison.md/json; no chip was activated in FPL.

## Calibration and risks

Five settled forecast weeks now include GW6: forecast 70 versus actual 36, Szoboszlai 86.2 minutes forecast versus 0 actual, van Ewijk 52.2 versus 90, Bruno 8.96 points versus 1. GW3–6 team forecasts exceeded actuals by 39.62, 20.30, 37.26 and 34.00 respectively. These describe recorded forecast lineups, not independently verified user scores or executed recommendations. Repeated attacking overprediction and minutes errors justify medium review confidence and caution with large optimizer uplifts. Latest calibration: 2.99 points MAE, 18.2 minutes MAE across five weeks. No scoring weights changed.

## Conditional route and chip calendar

GW8 Ajayi → Jay Dasilva; GW9 Schade → Dewsbury-Hall; GW10 Dubravka → Verbruggen; GW11 roll. All conditional and re-evaluated each week, not confirmed transfers. Keep reviewing whether Schade needs action sooner and whether a goalkeeper upgrade should take priority over bench repairs.

Engine calendar: Wildcard unassigned; Free Hit GW18 / GW17 backup (+7.2); Bench Boost GW11 / GW12 (+7.4); Triple Captain Haaland GW16 / GW19 (+10.0). Current Bench Boost +3.5 is weak. Current Triple Captain +9.3 is close to the later model +10.0; City rotation comments favour waiting. Official Scout also identifies Saka home to Hull in GW10 and Chelsea attackers against promoted sides in GW17–18 as alternatives. First-half chips expire at the GW19 deadline; do not wait for an assumed Double Gameweek. No confirmed double is a premise of this recommendation. GW16 fixture swings are a credible Wildcard reassessment point; unassigned must not mean indefinite postponement. Current Free Hit and Bench Boost windows are tentative given low uplifts and weak depth.

Changes from previous saved plan: advances GW6→7; reflects completed Tzolis→Schade move; replaces provisional GW7 double transfer with Szoboszlai→Groß; rewrites GW8–10 route; shifts Free Hit GW17→18, Bench Boost GW9→11 and Triple Captain GW7→16. Actual squad file remains at the user-confirmed pre-recommendation holdings.
