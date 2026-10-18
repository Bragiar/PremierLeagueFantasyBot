# Server deployment

Production path: `/home/bragi/apps/fpl-bot` on `bragi@192.168.1.241`.
This deployment is a Git checkout of `Bragiar/PremierLeagueFantasyBot`, independent
of the old OpenClaw checkout. Code and the squad are updated with `git pull --ff-only`;
there is no unattended code pull.
Keep `data/squad.yaml` current after making FPL moves. Never commit credentials.

The user systemd manager persists after logout (`Linger=yes`). A daily refresh at
06:00 UTC fetches official deadlines without AI. It programs an exact UTC timer
two hours before the next deadline. That run generates a Python recommendation,
calls subscription-authenticated `codex exec` with live web search in a read-only
temporary directory, then validates the shortlist selection again and sends Telegram.
The deadline reviewer is pinned to GPT-6.1 Sol with high reasoning and a
20-minute review timeout. Only web-tool event URLs count as verified sources. Two sources and high confidence
are required to override the engine. Any review failure retains the engine choices.
Retries are ten minutes apart; late catch-up stops fifteen minutes before deadline.
An exclusive process lock and the bot's persistent notification keys prevent
overlapping scheduler runs and duplicate delivery during normal operation.
As with any Telegram client, a crash after Telegram accepts a send but before local
state is saved can still cause a duplicate on retry.

Ignored server-only `config/strategy.local.yaml` overrides are merged with the tracked
`config/strategy.yaml`. `deploy/configure_server.py` creates these settings:

```yaml
notifications:
  offsets_minutes: [120]
  tolerance_minutes: 40
openai:
  enabled: false
codex:
  enabled: true
  binary: /home/bragi/apps/fpl-tools/node_modules/.bin/codex
  model: gpt-6.1-sol
  reasoning_effort: high
  timeout_seconds: 1200
runtime:
  directory: /home/bragi/apps/fpl-bot/.server/runtime
```

Live notification state, decision logs and generated plans live under
`~/apps/fpl-bot/.server/runtime/{state,logs,outputs}`. Git pulls cannot overwrite them.
The tracked state/output files are historical snapshots, not the live server state.
The scheduler strips API keys. Codex receives neither Telegram nor FPL credentials.
Codex reuses the server's saved ChatGPT CLI login. Login expiry and subscription
limits can interrupt research; the Python recommendation remains available.
The desktop app does not need to be running. The server must be powered on,
awake, connected, and able to reach FPL, ChatGPT and Telegram.

Install the three supplied units in `~/.config/systemd/user/`, then run the
refresh service before enabling `fpl-refresh.timer`. The refresh creates and
enables `fpl-deadline.timer`. Do not run a second production sender concurrently.

Useful checks:

```sh
systemctl --user list-timers 'fpl-*' --all
systemctl --user status fpl-deadline.service fpl-refresh.service
journalctl --user -u fpl-deadline.service -u fpl-refresh.service -n 60
cat ~/apps/fpl-bot/.server/scheduler_status.json
~/apps/fpl-bot/.venv/bin/python -m fpl_bot.server_scheduler --repo-root ~/apps/fpl-bot --inspect
```

Stop delivery: `systemctl --user disable --now fpl-refresh.timer fpl-deadline.timer`.
Also stop an active `fpl-deadline.service` before maintenance. Preserve `.env`,
`~/.codex/auth.json`, and `.server/runtime/state/last_run.json`, and `config/strategy.local.yaml`. Do not
overwrite server state with an older local copy during future deployments. Back up state and decision logs.

## Updating from this computer

Commit and push local changes, then run on the server:

```sh
cd ~/apps/fpl-bot
git pull --ff-only
.venv/bin/python -m pip install -e .
systemctl --user start fpl-refresh.service
```

For changes to running scheduler code, first stop both timers and wait for any
active deadline service to finish. Update the service definitions if changed,
reload systemd, then restart `fpl-refresh.timer` and the refresh service. Never
reset or delete `.server`, the private `.env`, or the server's ChatGPT login.

## Weekly strategy audit

`fpl-weekly-audit.timer` runs Tuesdays at 09:00 Europe/Amsterdam (including DST).
Install it and `fpl-weekly-audit.service` alongside the deadline units. It uses
ChatGPT-authenticated `gpt-6.1-sol` with `model_reasoning_effort="high"`; no API key.
The model receives an allowlisted packet of source/tests, tracked strategy/squad
and live runtime history. It has web search, no shell tools, and a read-only
sandbox. Python saves the report to `.server/runtime/outputs/strategy_review.md`
and status to `.server/runtime/state/weekly_audit.json`. Reports propose changes;
Python publishes a changed report to GitHub main as `outputs/strategy_review.md`.
There is no automatic strategy editing, FPL action or Telegram delivery.
A no-change result preserves the previous report. Failures preserve the report
and retry after 30 minutes, limited to three starts per three hours. Weekly
success is deduplicated. The deadline lock and a 45-minute exclusion before a
planned deadline run give production delivery priority. Raw audit web events are
private under runtime outputs. The audit can only assess the provided evidence;
it does not run tests or refresh the authenticated squad.

Enable: `systemctl --user enable --now fpl-weekly-audit.timer`.
Check: `systemctl --user status fpl-weekly-audit.timer fpl-weekly-audit.service`.
Stop: `systemctl --user disable --now fpl-weekly-audit.timer` (also stop its service
if an audit is active). The old Mac squad-sync and weekly audit automations are paused.

The server has a write-enabled deploy key restricted to this repository. The
private key stays at `~/.ssh/fpl_audit_ed25519`; GitHub host keys are in
`~/.ssh/fpl_github_known_hosts`, obtained through GitHub's authenticated HTTPS
metadata endpoint. Enable publication using the ignored local override:

```yaml
weekly_audit:
  publish:
    enabled: true
    ssh_key: /home/bragi/.ssh/fpl_audit_ed25519
    known_hosts: /home/bragi/.ssh/fpl_github_known_hosts
```

Publication clones current main into a disposable directory and commits only
`outputs/strategy_review.md`. A normal, non-forced push retries against fresh
main on a race; it never stages the production checkout or copies private files.
Unchanged reports produce no commit. Publication retries reuse the completed
weekly audit rather than spending model usage again. Status records the published
commit. The active production checkout intentionally does not pull new source
unattended; report commits can leave it behind origin until the next manual pull.
The report commit includes `[skip ci]`. Raw web events and runtime state stay private.
To revoke publishing, remove the GitHub deploy key and set `publish.enabled: false`.
