# FPL recommendation bot

This repository runs a recommendation-only Fantasy Premier League assistant. It reads the public, official FPL API, evaluates the tracked squad, validates the rules, writes an auditable decision record, and can send a concise Gameweek plan to Telegram. It never signs into an FPL account and never makes a transfer, lineup, captain, or chip change for you.

The deterministic Python analysis works without OpenAI. If `OPENAI_API_KEY` is present, the [OpenAI Responses API](https://developers.openai.com/api/reference/resources/responses/methods/create) reviews the engine's legal shortlist with web search, reports risks and sources, and can select a different shortlisted option only under the guarded policy below.

## What is included

- Python 3.12 package under `src/fpl_bot/`
- Official players, prices, availability, news, events, deadlines, fixtures, and fixture difficulty
- Five-Gameweek scoring (configurable up to six), combining official expected points,
  fixture difficulty, expected minutes, regressed form, xG/xA/xGI and defensive contributions
- A rolling, reachable 5–6 Gameweek route that carries the squad, bank, selling prices,
  free transfers, lineups and captains from one deadline into the next
- A provisional primary and backup window for every available chip before its
  half-season expiry, with one-chip-per-Gameweek collision checks
- A ranked shortlist containing “roll” plus the strongest legal transfer alternatives
- A chip shortlist with calculated Triple Captain and Bench Boost uplift plus legal
  Free Hit and Wildcard squad optimization
- Current web research for injuries, expected lineups, role changes, rotation and expert analysis
- Conservative transfer, captain, lineup, bench, and chip recommendations
- Separate scoring horizons: transfers use the configured multi-Gameweek plan, while
  lineup, bench order, captain, and vice-captain use only the immediate Gameweek
- Budget, position, 15-player, and maximum-three-per-club validation
- Alerts near 24 hours, 3 hours, and 45 minutes before the official API deadline
- Persistent per-window duplicate prevention
- Safe no-transfer fallback when live inputs cannot be trusted
- JSON Lines decision history plus a readable latest plan
- A machine-readable latest route and a saved prior route so each run explains what changed
- A saved forecast ledger that grades expected points and minutes against official results
- Deadline-driven Linux server scheduling with subscription Codex research and Telegram delivery

## 1. Run locally

Install Python 3.12, open a terminal in this folder, and run:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
cp .env.example .env
pytest
fpl-bot --dry-run --force --no-openai
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead. A forced dry run fetches current public data and writes a plan without contacting Telegram. A normal `fpl-bot` run exits without changing files unless one of the configured deadline windows is active.

Your editable inputs are:

- `data/squad.yaml`: the squad, bank, free transfers, purchase prices, captain,
  vice-captain, and chip availability for both half-seasons
- `config/strategy.yaml`: horizon, risk thresholds, notification offsets, and optional AI settings

After you actually make a transfer yourself, update `data/squad.yaml`. Set each player's `purchase_price` to the price you paid and update `bank` and `free_transfers`; that lets the bot apply FPL's half-profit selling-price rule correctly. A `null` purchase price is safe only for an untouched opening-squad player, where the bot reconstructs the opening price from the official season price change. After using a chip, change its status from `available` to `used` in the applicable half-season. Do not put credentials in either file.

### Optional authenticated local squad sync

The local sync reads your own FPL team and updates `data/squad.yaml`; it never submits
transfers, lineup changes, captaincy, or chips. Authentication is stored in macOS
Keychain, not in this repository. Do not paste a token into chat, a file, or a command
argument.

To obtain the one-time refresh token:

1. Sign in to FPL in Chrome and open the FPL site.
2. Open Chrome Developer Tools, choose **Application → Local Storage**, and select
   `https://fantasy.premierleague.com`.
3. Find the row whose **Key** begins with
   `oidc.user:https://account.premierleague.com/as:`. Double-click its **Value** cell
   on the right, which is a long JSON object beginning with `{`, then press
   <kbd>Command</kbd>+<kbd>A</kbd> and <kbd>Command</kbd>+<kbd>C</kbd>. Copy that entire
   Value cell—not the Key cell, `session_state`, `sub`, or another short field. The
   setup command safely extracts its `refresh_token`; treat the copied JSON like a
   password.
4. Find the numeric entry ID in an FPL URL such as `/entry/1234567/event/2`.
5. Run the setup command below. Paste the token only into its hidden prompt:

```bash
fpl-bot setup-fpl-auth --entry-id 1234567
```

The hidden prompt displays no characters when pasting. Alternatively, immediately
after copying the JSON Value cell, let the setup read it from the macOS clipboard and
clear the clipboard afterward:

```bash
fpl-bot setup-fpl-auth --entry-id 1234567 --from-clipboard
```

The setup immediately exchanges and verifies the token, then saves the rotated token
in macOS Keychain. Synchronize and validate the current team with:

```bash
fpl-bot sync-team
fpl-bot --preview --force --no-openai
```

Each sync retrieves exact FPL purchase prices, bank, remaining free transfers, captain,
vice-captain, and explicit chip statuses. It records detected player changes in
`logs/actual_transfer_history.jsonl`. If authorization expires, repeat the setup step.

If macOS Keychain is unavailable, the sync also accepts a local fallback file outside
the repository at `~/Library/Application Support/fpl-bot/auth.env`:

```dotenv
FPL_ENTRY_ID=1234567
FPL_REFRESH_TOKEN=your-refresh-token
```

Create that file with restrictive permissions and never commit or paste its contents
into chat. Keychain values remain preferred when readable, and the fallback file is
used only when Keychain access fails or the requested item is absent.

### How the decision model works

The bot does look at upcoming matches as well as FDR. For each player it builds an
immediate-Gameweek projection and a separate multi-Gameweek score. Official expected
points are the main early-season prior; form and points per match earn more influence
only as minutes accumulate. Fixture count and difficulty, availability, projected
minutes, xG/xA/xGI and defensive contributions then adjust that prior. This prevents a
single opening-week haul or a cheap zero-minute player from dominating the output.

Transfers are judged by the improvement to the legal squad over the full horizon, not
just by comparing two isolated player totals. An optional early-season move is held back
until there is enough evidence unless its projected gain is exceptional. Lineup and
captain decisions use the current Gameweek only. Captaincy has a minimum expected-minutes
gate and reports the margin over the second choice, so “High” now means more than simply
having no injury flag.

The immediate search considers every possible outgoing player and can recommend a
two-transfer bundle when two free transfers are available and the second move adds a
meaningful extra gain. Bench-only improvements receive only a small bench-coverage
weight, while upgrades that enter the best XI receive their full value. Price-rise and
price-fall forecasts are shown as timing warnings and tie-breakers; transfer momentum
never creates expected points by itself. The shortlist also exposes one squad-health
move and one market-watch move when available, making weak-minute players and popular
targets visible without allowing either signal to override the football projection.

Forced runs more than five days before a deadline now select a transfer hold while
still listing legal candidates. This leaves room for international-duty and press
conference news; a reviewed `--select-option` choice bypasses the timing hold. The
planner places more value on usable bench cover, and recent form is smoothed against
season points per match rather than taking whichever number is higher.
Three consecutive large forecast overshoots for a proposed captain lower confidence
and add a deadline review warning; they do not automatically force a different captain.

If Python cannot reach the official FPL API in a local sandbox, the engine can read
fresh, manually fetched official JSON using `FPL_SNAPSHOT_DIR`. Place files at paths
such as `bootstrap-static.json`, `fixtures.json`, and `event/5/live.json` beneath that
directory. Every file must be less than 30 minutes old. Never use this mode with an
old snapshot for a deadline decision.

Ownership is not treated as expected points. `mini_league_mode: balanced` maximizes the
model projection. `protect` adds only a small ownership tie-break when defending a lead;
`chase` slightly favors a lower-owned captain only when the expected-points decision is
already close. Keep `balanced` unless league position gives a clear reason to change it.

Chip projections are incremental versus the normal plan. Triple Captain adds one extra
copy of the captain projection; Bench Boost adds the four substitute projections; Free
Hit runs a bounded search for a legal one-Gameweek squad; Wildcard does the same for a
permanent squad over the configured horizon. These are heuristic estimates rather than
proof of the globally optimal squad. With `save_chips_by_default: true` and
`allow_exceptional_early_chip: false`, automatic selection saves chips before expiry
pressure even if their displayed gain exceeds the exceptional threshold. A no-chip
selection is therefore a policy decision, not proof that waiting scores better.

`wildcard_review_enabled: true` separately tests Wildcard now, Wildcard next week
(after the selected shortlisted transfer or a hold), and ordinary transfer routes.
Every route uses the same horizon, weekly projections, budget and transfer rules.
Rebuilds optimize a separate legal XI and captain each week, use several starting
structures, and test retaining the selected captain. Players retained on a chip are
valued at their selling opportunity cost, rather than charged a market repurchase.
The outputs are `outputs/latest_wildcard_review.md` and `.json`. These comparisons
do not activate a chip or replace the reviewed immediate shortlist. Drafts remain
experimental until selected through the normal validated flow.

The scores do not price the value of retaining a Wildcard beyond the horizon, and
future prices, injury recovery and rotation remain uncertain. The search is bounded;
it does not enumerate every team or prove global optimality. Increase
`optimizer_anchor_seeds` or `wildcard_review_state_searches` to explore more starting
structures or pre-Wildcard states at a higher runtime cost. Keep forecast weights
unchanged until held-out, chronological evaluation supports a change.

### Rolling short-term and long-term planning

The immediate recommendation remains guarded by the legal transfer/chip shortlist. Once
that current action is selected, the rolling planner searches reachable future states
rather than constructing an impossible independent dream team for every Gameweek. Each
state carries the 15-player squad, bank, purchase prices and free transfers into the next
deadline. It can roll up to five free transfers, use up to two in a planned week, and
subtract configured points hits. Wildcard and Free Hit routes preserve already banked
transfers, matching the current official rules.

The exact route covers the configured 5–6 Gameweek horizon. Current FPL expected-points
data is used for the immediate week; future weeks use a regressed blend of price, form,
minutes, availability and fixture difficulty so one early result does not dominate the
whole route. The search is bounded and therefore optimal only within its candidate pool
and projection model. It assumes current player prices; rerunning after each deadline is
essential.

The longer chip calendar runs to GW19 or GW38 and assigns distinct primary and backup
windows for every available chip. Long-range targets are deliberately labelled low or
medium confidence because cup results, Blank/Double Gameweeks, injuries and player roles
can change. A rejected current chip is not silently reintroduced into the same
Gameweek's long-term calendar. Free Hit is not assigned to an ordinary distant week just
because an optimized squad scores better: the planner waits for meaningful blanks,
doubles or genuine expiry pressure. If there is no credible window, a chip is explicitly
shown as unassigned rather than forcing a misleading date.

Every preview refreshes `outputs/latest_strategy_plan.json` and embeds the route in
`outputs/latest_recommendation.md`. A recorded dry run or Telegram run also saves the
baseline to `state/rolling_plan.json`; the following run compares against it and lists
material transfer, captain and chip-window changes.

### Run the hybrid review inside this app without API charges

Open this FPL folder in a fresh Codex/ChatGPT task and say:

> Run the FPL review here without calling the OpenAI API.

The repository's `AGENTS.md` tells Codex to generate a non-recording Python preview with OpenAI disabled, inspect the legal shortlist, research current news using the app's web search, choose only a shortlisted option, and send that option back through Python for final validation. The finalized run is dry-run only, so it records the recommendation but never sends Telegram.

This avoids charges to your separate OpenAI API account; ordinary ChatGPT/Codex plan limits still apply. `openai.enabled` is disabled by default in `config/strategy.yaml`, so the Python bot never calls that API even if a key exists. The server instead uses its separately configured subscription Codex reviewer. Set it to `true` only if you deliberately want the bot-hosted web review again.

To exercise Telegram too, say:

> Run the FPL review here without calling the OpenAI API, then send the final plan to Telegram as a test.

Codex will use `--test-telegram`. The real message begins with `TEST ONLY`, its decision-log delivery is recorded as `test_sent`, and it does not mark the Gameweek notification window as delivered. Therefore, a later real deadline notification is not suppressed.

## 2. Create a Telegram bot and get the chat ID

1. In Telegram, start a chat with **@BotFather**.
2. Send `/newbot`, choose a name, and copy the bot token. Treat it like a password.
3. Open your new bot and send it a message such as `hello`.
4. In a browser, visit `https://api.telegram.org/botYOUR_TOKEN/getUpdates`.
5. Find `message.chat.id` in the response. That number (which may be negative for a group) is the chat ID.
6. For local use only, put the values in `.env` as `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. `.env` is ignored by Git.

Test delivery only when you are ready to send a real message:

```bash
fpl-bot --force --no-openai --test-telegram
```

The default dry run never sends Telegram, even if credentials are present.

## 3. Create the GitHub repository and add secrets

Create an empty private repository on GitHub without adding a README or `.gitignore`. Then connect this local repository, replacing the placeholder URL:

```bash
git remote add origin https://github.com/YOUR_NAME/YOUR_REPOSITORY.git
git push -u origin main
```

In GitHub, open **Settings → Secrets and variables → Actions → Repository secrets** and add:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `OPENAI_API_KEY` (optional)

Use **repository secrets** for the normal setup. The manually dispatched workflow can access them
without declaring a deployment environment. Use **environment secrets** only if you
intentionally configure separate environments such as `production` and `staging`, need
different credentials for each, or want environment approval and branch-protection
rules. In that case, the workflow job must also reference the matching environment.

To change the optional model, add an Actions **variable** named `OPENAI_MODEL`. The workflow defaults to `gpt-5.6-sol`. Never paste a secret into workflow YAML, logs, issues, or commits.

Under **Settings → Actions → General → Workflow permissions**, allow **Read and write permissions** so the workflow can commit its generated decision and planning artifacts. Branch protection must also permit the built-in GitHub Actions bot to push to the chosen branch, or use a narrowly scoped approved alternative.

## 4. Manual GitHub Actions fallback

The workflow in `.github/workflows/fpl-bot.yml` retains manual dispatch for emergency use. Its cron trigger has been removed because the server is the production scheduler. Avoid running a second live sender against independent notification state.

For the first test:

1. Choose **Run workflow**.
2. Leave **dry_run** enabled.
3. Leave **force** disabled; dry runs are automatically forced so they produce a plan immediately.
4. Start the run and inspect `outputs/latest_recommendation.md` and the newest line in `logs/decision_log.jsonl`.

Then run a real forced notification only if you want a Telegram message: disable **dry_run** and enable **force**. Normal production delivery runs on the server two hours before each deadline. GitHub no longer polls for deadlines.

The workflow has one concurrency group per branch, does not cancel an in-progress run, and is triggered only by manual dispatch. Its own commits therefore do not start another bot run. A notification is marked delivered only after Telegram accepts it.

## 5. Decision log lifecycle

Every generated plan has four related pieces:

1. `data/squad.yaml` and `config/strategy.yaml` are the human-maintained inputs.
2. `outputs/latest_recommendation.md` and `outputs/latest_strategy_plan.json` are replaced
   with the newest readable and machine-readable plans.
3. `logs/decision_log.jsonl` receives one immutable JSON object per decision, including the engine shortlist, rolling route, chip calendar, web-research verdict and sources, validation, delivery result, fallback status, and whether optional AI research was used. Credentials are never recorded.
4. `state/last_run.json` keeps delivered notification keys and the last known future deadlines. `state/rolling_plan.json` keeps the last recorded route for change detection. A dry run records its result but does not claim a notification window. A successful Telegram send claims `gwN:24h`, `gwN:3h`, or `gwN:45m`, preventing duplicates.
5. `state/forecast_history.json` stores the final projection for each Gameweek. Once the
   official event is finished, the next run records points error, minutes error,
   projected-versus-actual XI points and expected-starter hit rate. The recent summary is
   surfaced in validation so model changes can be based on measured misses rather than
   memory. It deliberately does not auto-tune weights from a tiny sample.

GitHub Actions commits only the decision log, notification state, saved rolling plan,
forecast ledger, latest recommendation, and machine-readable latest plan. Old notification
keys are pruned after their Gameweek has safely passed. If Telegram fails, the failure is
recorded but the window is not marked sent, so a later scheduled run can retry while the
window remains open.

JSON Lines is deliberately append-only and Git-friendly: each line is a complete record that can be reviewed or analyzed independently. Do not hand-edit old decisions; correct future inputs and let the next run create a new record.

### Web-research decision policy

Python always creates and validates the transfer and chip shortlists first. The research model must use web search and may choose only exact IDs from those shortlists. Model-written URLs are discarded unless they also appear in the API's web-search source metadata. A researched combination replaces the engine's initial choices only when the verdict is `disagree`, confidence is `high`, at least two sources are verified, and `allow_research_override` remains enabled. The transfer and chip combination is then rebuilt and validated by Python. Any API, parsing, sourcing or validation failure safely retains the deterministic choices.

Configure the candidate count, search-call limit, override switch and minimum source count in `config/strategy.yaml`. Use `--no-openai` to skip the bot-hosted OpenAI API review. The separate server-only `codex.enabled` setting controls subscription-authenticated CLI research.

## 6. Server scheduling and Codex review

Production runs on `bragi@192.168.1.241` in `/home/bragi/apps/fpl-bot`.
The server runs Debian Linux. A daily lightweight systemd task refreshes official
FPL deadlines and programs the next run for two hours before the next deadline.
Python generates the engine plan and invokes `codex exec` using the server's
ChatGPT login, with live web search and shell commands disabled. No OpenAI API key
is used. Subscription usage limits still apply.

The reviewer receives the legal shortlist, expected minutes, confidence notes,
rolling plan, chip calendar and forecast history. Python verifies source URLs
against web-tool events, applies the conservative override policy, revalidates
budget and squad rules, and sends Telegram. If review fails, the engine choices
remain. Delivery failures retry after ten minutes, with deadline and duplicate
guards. A missed run can catch up until fifteen minutes before the deadline.

The server must remain powered on, awake and connected; the desktop app can be
closed. Keep the server's squad file current after making FPL changes. Server
state and logs in `.server/runtime/` are authoritative and preserved across code pulls.
Ignored `config/strategy.local.yaml` overrides retain the server settings.
GitHub retains manual dispatch as an emergency alternative; its cron is removed.
See [server operating instructions](deploy/README.md) for status, logs and recovery.

The separate weekly Codex maintenance task may review strategy and tests. It
must not send Telegram or become a second deadline scheduler. Its local files
do not automatically sync with the server deployment.

## Safety and operating notes

- This is advice, not an automatic FPL manager. The optional authenticated sync is read-only and never changes the team on FPL. Confirm injuries, press-conference news, and the final deadline yourself.
- The public FPL API does not reveal your private bank, purchase prices, free transfers, or whether you acted on a recommendation. Keep `data/squad.yaml` current manually or with the authenticated local sync.
- The refresh token is an account credential. Keep it in macOS Keychain, never commit it, and renew it if authentication is rejected.
- Official FPL news and chance-of-playing fields can downgrade or exclude players from recommendations; a live-data error produces a low-confidence, no-transfer, no-hit fallback with the configured captaincy and a legal 4-4-2.
- Web research is advisory evidence, not guaranteed truth. The output records its links and risks so you can inspect late news yourself.
- Production notification timing is two hours before the deadline plus plan/research runtime. Daily refreshes catch deadline changes. Server downtime, connectivity loss or exhausted subscription limits can affect delivery or research; the bot cannot send after the deadline.
- Run `pytest` after strategy or code changes. Run `fpl-bot --dry-run --force` before merging operational changes.

## Project map

```text
src/fpl_bot/                  service code
config/strategy.yaml         strategy and notification preferences
data/squad.yaml              tracked team state
logs/decision_log.jsonl      append-only audit history
logs/actual_transfer_history.jsonl completed moves detected by authenticated sync
outputs/latest_recommendation.md
outputs/latest_strategy_plan.json
outputs/strategy_review.md
state/last_run.json           duplicate prevention and last known deadlines
state/rolling_plan.json       previous route used for change detection
state/forecast_history.json   predictions settled against official results
tests/                        focused automated checks
.github/workflows/fpl-bot.yml manual emergency fallback
deploy/                       server units and operating instructions
```
