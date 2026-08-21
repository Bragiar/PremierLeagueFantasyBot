from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

from fpl_bot.service import run


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def parse_now(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a recommendation-only FPL deadline plan."
    )
    parser.add_argument(
        "--repo-root", type=Path, default=default_repo_root(), help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate and record a plan without sending Telegram.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Generate now even when no notification window is due.",
    )
    parser.add_argument(
        "--no-openai",
        action="store_true",
        help="Skip optional OpenAI commentary even when a key is configured.",
    )
    parser.add_argument(
        "--now",
        type=parse_now,
        default=None,
        help="Override the current UTC time (intended for testing).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    load_dotenv(repo_root / ".env")
    try:
        result = run(
            repo_root,
            dry_run=args.dry_run,
            force=args.force,
            now=args.now,
            disable_openai=args.no_openai,
        )
    except (OSError, ValueError) as exc:
        print(f"FPL bot stopped safely: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(result.message)
    return result.exit_code
