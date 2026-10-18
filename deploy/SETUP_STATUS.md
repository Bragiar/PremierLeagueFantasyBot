# Setup status — 18 October 2026

Production cutover is complete.

- Server: `bragi@192.168.1.241`, Debian 13, host `old-macbook-server`.
- Deployment: `/home/bragi/apps/fpl-bot`; independent of the OpenClaw checkout.
- Codex CLI 0.163.0 uses a direct ChatGPT device login completed by the user.
  No existing Codex login file was copied to the server. No OpenAI API key is used.
- The server holds only the Telegram credentials needed by Python; both `getMe`
  and `getChat` succeeded. Credential files have mode 600.
- All 82 tests passed on the Mac and server with the repository test configuration.
- A live-data reviewed preview completed successfully: source `deterministic+codex-web`,
  six research sources, with source URLs verified against real web-tool events.
  The review retained `hold` and `chip:none`; this was a setup preview, not a deadline decision.
- Both user systemd timers are active and enabled; `Linger=yes` persists after logout.
- Daily lightweight refresh: 06:00 UTC. No AI runs during deadline refresh.
- Next researched plan starts: GW8, 23 October 2026 at 15:30 UTC / 17:30 Amsterdam,
  two hours before the 17:30 UTC / 19:30 Amsterdam deadline. Delivery follows computation.
- Python validates reviewed choices and sends Telegram. Review failures retain the engine
  choices; delivery failures retry with normal deadline and duplicate guards.
- GitHub cron removed; manual dispatch retained. Verified no queued or running workflow
  at cutover. Commit: `be9347b810f95bef56edb27e14248c49647c0014`.
- No Telegram message was sent during setup.

Operations: see `deploy/README.md`. Keep the server squad file current after FPL moves.
The complete local source, squad updates, tests and saved reviews are committed
to GitHub. The active server deployment is a Git checkout of the same revision.
Server overrides are ignored in `config/strategy.local.yaml`; live state, logs and
outputs are preserved in `.server/runtime/` outside tracked files. Update code
with `git pull --ff-only`. Server runtime data remains authoritative.
