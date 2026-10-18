import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from fpl_bot import weekly_audit


def setup(monkeypatch, tmp_path):
    runtime = tmp_path / ".server/runtime"
    monkeypatch.setattr(weekly_audit, "load_strategy", lambda _: {
        "runtime": {"directory": str(runtime)}, "codex": {"binary": "codex"}})
    report = runtime / "outputs/strategy_review.md"
    report.parent.mkdir(parents=True)
    report.write_text("previous review")
    return runtime, report


def test_audit_packet_uses_live_history_and_excludes_private_files(tmp_path):
    runtime = tmp_path / ".server/runtime"
    (runtime / "logs").mkdir(parents=True)
    (runtime / "logs/decision_log.jsonl").write_text('live history')
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs/decision_log.jsonl").write_text('old history')
    (tmp_path / ".env").write_text('secret')
    (tmp_path / "config").mkdir()
    (tmp_path / "config/strategy.local.yaml").write_text('private override')
    packet = json.dumps(weekly_audit.audit_packet(tmp_path, runtime))
    assert 'live history' in packet
    assert 'old history' not in packet
    assert 'secret' not in packet
    assert 'private override' not in packet


def test_timeout_preserves_report_and_strips_credentials(monkeypatch, tmp_path):
    runtime, report = setup(monkeypatch, tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "secret")
    def fail(command, **kwargs):
        assert 'OPENAI_API_KEY' not in kwargs['env']
        assert 'TELEGRAM_CHAT_ID' not in kwargs['env']
        assert command[command.index('--model') + 1] == 'gpt-6.1-sol'
        assert 'model_reasoning_effort="high"' in command
        raise subprocess.TimeoutExpired(command, 1800)
    monkeypatch.setattr(weekly_audit.subprocess, 'run', fail)
    with pytest.raises(RuntimeError, match='previous report preserved'):
        weekly_audit.run_audit(tmp_path)
    assert report.read_text() == 'previous review'
    assert json.loads((runtime / 'state/weekly_audit.json').read_text())['status'] == 'failed'


def test_no_change_retains_report_and_deduplicates_week(monkeypatch, tmp_path):
    runtime, report = setup(monkeypatch, tmp_path)
    calls = []
    def run(command, **kwargs):
        calls.append(command)
        Path(command[command.index('-o') + 1]).write_text('NO_CHANGE')
        return SimpleNamespace(stdout='')
    monkeypatch.setattr(weekly_audit.subprocess, 'run', run)
    assert 'no_change' in weekly_audit.run_audit(tmp_path)
    assert 'Already audited' in weekly_audit.run_audit(tmp_path)
    assert len(calls) == 1
    assert report.read_text() == 'previous review'
