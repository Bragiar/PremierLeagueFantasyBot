"""Publish only the weekly report from a disposable checkout of current main."""
from __future__ import annotations

import os
from pathlib import Path
import shlex
import subprocess
import tempfile

FETCH_URL = "https://github.com/Bragiar/PremierLeagueFantasyBot.git"
PUSH_URL = "git@github.com:Bragiar/PremierLeagueFantasyBot.git"
REPORT_PATH = "outputs/strategy_review.md"


def publish_report(report: Path, config: dict) -> str:
    if not config.get("enabled", False):
        return "disabled"
    content = report.read_text(encoding="utf-8")
    if not content.strip():
        raise ValueError("Cannot publish an empty audit")
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("GIT_") and not any(
               part in k.upper() for part in ("TOKEN", "SECRET", "PASSWORD", "API_KEY"))}
    env["GIT_TERMINAL_PROMPT"] = "0"
    key = Path(config["ssh_key"]).expanduser()
    env["GIT_SSH_COMMAND"] = (
        "ssh -i " + shlex.quote(str(key)) + " -o IdentitiesOnly=yes -o BatchMode=yes"
    )
    if config.get("known_hosts"):
        env["GIT_SSH_COMMAND"] += " -o UserKnownHostsFile=" + shlex.quote(
            str(Path(config["known_hosts"]).expanduser()))
    # A rejected non-fast-forward push retries against fresh main. Never reset the
    # production checkout, force-push, stage other files or copy live state.
    for attempt in range(3):
        with tempfile.TemporaryDirectory(prefix="fpl-audit-publish-") as folder:
            work = Path(folder) / "repo"
            def git(*args: str) -> subprocess.CompletedProcess:
                return subprocess.run(
                    ["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                     "-c", "user.name=FPL weekly audit", "-c", "user.email=fpl-audit@users.noreply.github.com",
                     *args], env=env, capture_output=True, text=True, timeout=90, check=True)
            git("clone", "--depth", "1", "--single-branch", "--branch", "main", "--no-tags", FETCH_URL, str(work))
            target = work / REPORT_PATH
            if target.is_symlink():
                raise ValueError("Refusing a symlink report target")
            if target.exists() and target.read_text(encoding="utf-8") == content:
                return "unchanged"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            git("-C", str(work), "add", "--", REPORT_PATH)
            git("-C", str(work), "commit", "-m", "docs: update weekly FPL strategy audit [skip ci]")
            commit = git("-C", str(work), "rev-parse", "HEAD").stdout.strip()
            try:
                git("-C", str(work), "push", PUSH_URL, "HEAD:refs/heads/main")
                return commit
            except subprocess.CalledProcessError:
                if attempt == 2:
                    raise RuntimeError("Audit publication failed after three push attempts") from None
    raise RuntimeError("Audit publication failed")
