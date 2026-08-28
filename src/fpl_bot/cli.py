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
        "--preview",
        action="store_true",
        help="Generate latest output without Telegram, state changes, or a decision-log entry.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Generate now even when no notification window is due.",
    )
    parser.add_argument(
        "--no-openai",
        action="store_true",
        help="Skip optional OpenAI web research even when a key is configured.",
    )
    parser.add_argument(
        "--test-telegram",
        action="store_true",
        help="Send a clearly labelled test message without claiming a real notification window.",
    )
    parser.add_argument(
        "--select-option",
        default=None,
        help="Select an exact option ID from the engine shortlist and validate it again.",
    )
    parser.add_argument(
        "--select-chip",
        default=None,
        help="Select an exact option ID from the chip shortlist and validate it again.",
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
            preview=args.preview,
            test_telegram=args.test_telegram,
            force=args.force,
            now=args.now,
            disable_openai=args.no_openai,
            selected_option_id=args.select_option,
            selected_chip_id=args.select_chip,
        )
    except (OSError, ValueError) as exc:
        print(f"FPL bot stopped safely: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(result.message)
    return result.exit_code
