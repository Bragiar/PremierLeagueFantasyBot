"""Deadline-driven systemd runner; daily refreshes never invoke AI."""
from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
import fcntl
import json
import os
from pathlib import Path
import subprocess

from dotenv import load_dotenv

from fpl_bot.config import load_strategy
from fpl_bot.deadlines import event_from_dict, notification_key
from fpl_bot.fpl_api import FPLClient
from fpl_bot.storage import load_state, save_json_object


def next_wakeup(events: list[dict], state: dict, now: datetime,
                offset: int = 120) -> tuple[datetime, int] | None:
    sent = state.get("sent_notifications", {})
    for event in sorted((event_from_dict(e) for e in events if e.get("deadline_time")),
                        key=lambda e: e.deadline):
        # Leave enough time to generate, validate and deliver before the deadline.
        if event.deadline <= now + timedelta(minutes=15):
            continue
        if notification_key(event.id, f"{offset}m") in sent:
            continue
        return max(event.deadline - timedelta(minutes=offset), now + timedelta(seconds=15)), event.id
    return None


def write_timer(when: datetime) -> None:
    target = Path.home() / ".config/systemd/user/fpl-deadline.timer"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "[Unit]\nDescription=Next FPL deadline review\n\n[Timer]\n"
        f"OnCalendar={when.astimezone(UTC):%Y-%m-%d %H:%M:%S} UTC\n"
        "AccuracySec=1s\nPersistent=true\nUnit=fpl-deadline.service\n\n"
        "[Install]\nWantedBy=timers.target\n"
    )
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "--user", "enable", "fpl-deadline.timer"], check=True)
    subprocess.run(["systemctl", "--user", "restart", "fpl-deadline.timer"], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--run", action="store_true", help="Send only if the two-hour window is due")
    parser.add_argument("--inspect", action="store_true", help="Show next wakeup without changing timers")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    runtime = root / ".server"
    runtime.mkdir(exist_ok=True)
    with (runtime / "scheduler.lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("Another FPL run is already active.")
            return 0
        load_dotenv(root / ".env")
        for key in ("OPENAI_API_KEY", "CODEX_API_KEY"):
            os.environ.pop(key, None)
        config = load_strategy(root / "config/strategy.yaml")
        artifact_root = Path(config.get("runtime", {}).get("directory", root))
        if config["notifications"]["offsets_minutes"] != [120]:
            raise ValueError("Server runner requires a single 120-minute notification window")
        api = config["fpl_api"]
        events = FPLClient(api["base_url"], api.get("timeout_seconds", 20),
                           api.get("retries", 3)).bootstrap()["events"]
        state = load_state(artifact_root / "state/last_run.json")
        now = datetime.now(UTC)
        wakeup = next_wakeup(events, state, now)
        result_status = "refresh"
        failed = False
        if args.run and wakeup and wakeup[0] <= now + timedelta(seconds=20):
            from fpl_bot.service import run
            # No force: the normal duplicate and deadline guards remain active.
            result = run(root, disable_openai=True)
            print(f"FPL result: {result.status}", flush=True)
            result_status, failed = result.status, result.exit_code != 0
            state = load_state(artifact_root / "state/last_run.json")
            now = datetime.now(UTC)
            wakeup = next_wakeup(events, state, now)
            if failed and wakeup:
                wakeup = (max(wakeup[0], now + timedelta(minutes=10)), wakeup[1])
        status = {"checked_at": now.isoformat(), "result": result_status,
                  "next_run": wakeup[0].isoformat() if wakeup else None,
                  "event_id": wakeup[1] if wakeup else None}
        print(json.dumps(status), flush=True)
        if not args.inspect:
            save_json_object(runtime / "scheduler_status.json", status)
            if wakeup:
                write_timer(wakeup[0])
            else:
                subprocess.run(["systemctl", "--user", "stop", "fpl-deadline.timer"], check=False)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
