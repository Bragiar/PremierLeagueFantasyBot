"""Apply ignored server settings and preserve runtime data outside tracked files."""
from pathlib import Path
import shutil
import yaml

root = Path.home() / "apps/fpl-bot"
runtime = root / ".server/runtime"
runtime.mkdir(parents=True, exist_ok=True)
for name in ("state", "logs", "outputs"):
    destination = runtime / name
    if not destination.exists():
        if (root / name).exists():
            shutil.copytree(root / name, destination)
        else:
            destination.mkdir()
settings = {
    "notifications": {"offsets_minutes": [120]},
    "openai": {"enabled": False},
    "codex": {
        "enabled": True,
        "binary": str(Path.home() / "apps/fpl-tools/node_modules/.bin/codex"),
        "model": "gpt-6.1-sol",
        "reasoning_effort": "high",
        "timeout_seconds": 1200,
    },
    "runtime": {"directory": str(runtime)},
    "weekly_audit": {"publish": {
        "enabled": (Path.home() / ".ssh/fpl_audit_ed25519").is_file(),
        "ssh_key": str(Path.home() / ".ssh/fpl_audit_ed25519"),
        "known_hosts": str(Path.home() / ".ssh/fpl_github_known_hosts"),
    }},
}
(root / "config/strategy.local.yaml").write_text(yaml.safe_dump(settings, sort_keys=False))
print("Server overrides saved; runtime preserved outside tracked files.")
