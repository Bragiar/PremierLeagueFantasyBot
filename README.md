# FPL recommendation bot

This repository runs a recommendation-only Fantasy Premier League assistant. It reads the public, official FPL API, evaluates the tracked squad, validates the rules, writes an auditable decision record, and can send a concise Gameweek plan to Telegram. It never signs into an FPL account and never makes a transfer, lineup, captain, or chip change for you.

The deterministic Python analysis works without OpenAI. If `OPENAI_API_KEY` is present, the [OpenAI Responses API](https://developers.openai.com/api/docs/guides/text) adds a short explanation but cannot alter the validated plan.

## What is included

- Python 3.12 package under `src/fpl_bot/`
- Official players, prices, availability, events, deadlines, fixtures, and fixture difficulty
- Five-Gameweek scoring (configurable up to six), including defensive-contribution data
- Conservative transfer, captain, lineup, bench, and chip recommendations
- Budget, position, 15-player, and maximum-three-per-club validation
- Alerts near 24 hours, 3 hours, and 45 minutes before the official API deadline
- Persistent per-window duplicate prevention
- Safe no-transfer fallback when live inputs cannot be trusted
- JSON Lines decision history plus a readable latest plan
- GitHub Actions every 30 minutes and a separate local Codex strategy reviewer

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

- `data/squad.yaml`: the squad, bank, free transfers, purchase prices, captain, and vice-captain
- `config/strategy.yaml`: horizon, risk thresholds, notification offsets, and optional AI settings

After you actually make a transfer yourself, update `data/squad.yaml`. Set each player's `purchase_price` to the price you paid and update `bank` and `free_transfers`; that lets the bot apply FPL's half-profit selling-price rule correctly. Do not put credentials in either file.

## 2. Create a Telegram bot and get the chat ID

1. In Telegram, start a chat with **@BotFather**.
2. Send `/newbot`, choose a name, and copy the bot token. Treat it like a password.
3. Open your new bot and send it a message such as `hello`.
4. In a browser, visit `https://api.telegram.org/botYOUR_TOKEN/getUpdates`.
5. Find `message.chat.id` in the response. That number (which may be negative for a group) is the chat ID.
6. For local use only, put the values in `.env` as `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. `.env` is ignored by Git.

Test delivery only when you are ready to send a real message:

```bash
fpl-bot --force --no-openai
```

The default dry run never sends Telegram, even if credentials are present.

## 3. Create the GitHub repository and add secrets

Create an empty private repository on GitHub without adding a README or `.gitignore`. Then connect this local repository, replacing the placeholder URL:

```bash
git remote add origin https://github.com/YOUR_NAME/YOUR_REPOSITORY.git
git push -u origin main
```

In GitHub, open **Settings → Secrets and variables → Actions → Secrets** and add:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `OPENAI_API_KEY` (optional)

To change the optional model, add an Actions **variable** named `OPENAI_MODEL`. The workflow defaults to `gpt-5.6-sol`. Never paste a secret into workflow YAML, logs, issues, or commits.

Under **Settings → Actions → General → Workflow permissions**, allow **Read and write permissions** so the workflow can commit its three generated artifacts. Branch protection must also permit the built-in GitHub Actions bot to push to the chosen branch, or use a narrowly scoped approved alternative.

## 4. Enable and test GitHub Actions

Pushing the repository installs the workflow in `.github/workflows/fpl-bot.yml`. Open the **Actions** tab, select **FPL recommendation bot**, and enable workflows if GitHub asks.

For the first test:

1. Choose **Run workflow**.
2. Leave **dry_run** enabled.
3. Leave **force** disabled; dry runs are automatically forced so they produce a plan immediately.
4. Start the run and inspect `outputs/latest_recommendation.md` and the newest line in `logs/decision_log.jsonl`.

Then run a real forced notification only if you want a Telegram message: disable **dry_run** and enable **force**. Scheduled runs happen every 30 minutes. They first fetch the lightweight official deadline feed and exit quickly without modifying the repository when no window is due.

The workflow has one concurrency group per branch, does not cancel an in-progress run, and is triggered only by the schedule or manual dispatch. Its own commits therefore do not start another bot run. A notification is marked delivered only after Telegram accepts it.

## 5. Decision log lifecycle

Every generated plan has four related pieces:

1. `data/squad.yaml` and `config/strategy.yaml` are the human-maintained inputs.
2. `outputs/latest_recommendation.md` is replaced with the newest readable plan.
3. `logs/decision_log.jsonl` receives one immutable JSON object per decision, including the input window, validation, delivery result, fallback status, and whether optional AI prose was used. Credentials are never recorded.
4. `state/last_run.json` keeps delivered notification keys and the last known future deadlines. A dry run records its result but does not claim a notification window. A successful Telegram send claims `gwN:24h`, `gwN:3h`, or `gwN:45m`, preventing duplicates.

GitHub Actions commits only the decision log, state, and latest recommendation. Old notification keys are pruned after their Gameweek has safely passed. If Telegram fails, the failure is recorded but the window is not marked sent, so a later scheduled run can retry while the window remains open.

JSON Lines is deliberately append-only and Git-friendly: each line is a complete record that can be reviewed or analyzed independently. Do not hand-edit old decisions; correct future inputs and let the next run create a new record.

## 6. Codex as the AI maintainer

The local Codex scheduled task runs daily against this project. It reviews new decision-log entries, compares outcomes and assumptions with `config/strategy.yaml`, and writes a concise review to `outputs/strategy_review.md`. It may recommend changes, but it must not send Telegram, edit credentials, log into FPL, or become the deadline scheduler.

GitHub Actions remains the dependable production runner because it checks official deadlines every 30 minutes even when this computer or Codex is closed. Codex is the slower maintenance layer: use it to review the repository, improve tests, investigate weak assumptions, and propose carefully validated strategy changes. Commit any accepted strategy review or code change normally.

## Safety and operating notes

- This is advice, not an automatic FPL client. Confirm injuries, press-conference news, and the final deadline yourself.
- The public FPL API does not reveal your private bank, purchase prices, free transfers, or whether you acted on a recommendation. Keep `data/squad.yaml` current.
- A live-data error produces a low-confidence, no-transfer, no-hit fallback with the configured captaincy and a legal 4-4-2.
- Notification timing is approximate because GitHub schedules can be delayed. The default 40-minute tolerance is designed for a 30-minute schedule.
- Run `pytest` after strategy or code changes. Run `fpl-bot --dry-run --force` before merging operational changes.

## Project map

```text
src/fpl_bot/                  service code
config/strategy.yaml         strategy and notification preferences
data/squad.yaml              tracked team state (no FPL login)
logs/decision_log.jsonl      append-only audit history
outputs/latest_recommendation.md
outputs/strategy_review.md
state/last_run.json           duplicate prevention and last known deadlines
tests/                        focused automated checks
.github/workflows/fpl-bot.yml production schedule
```
