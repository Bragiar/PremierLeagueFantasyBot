from pathlib import Path
import subprocess

from fpl_bot import audit_publish


def git(*args):
    return subprocess.run(['git', *args], check=True, capture_output=True, text=True).stdout.strip()


def test_publishes_only_report_on_latest_main_and_preserves_local_checkout(tmp_path, monkeypatch):
    remote = tmp_path / 'remote.git'
    git('init', '--bare', str(remote))
    seed = tmp_path / 'seed'
    git('init', '-b', 'main', str(seed))
    git('-C', str(seed), 'config', 'user.name', 'Test')
    git('-C', str(seed), 'config', 'user.email', 'test@example.com')
    (seed / 'source.txt').write_text('newer source changes')
    git('-C', str(seed), 'add', 'source.txt')
    git('-C', str(seed), 'commit', '-m', 'existing main')
    git('-C', str(seed), 'push', str(remote), 'main')
    production = tmp_path / 'production'
    production.mkdir()
    (production / '.env').write_text('private token')
    (production / 'unrelated.txt').write_text('local edits')
    report = production / 'review.md'
    report.write_text('Reviewed the chip plan.\n')
    monkeypatch.setattr(audit_publish, 'FETCH_URL', str(remote))
    monkeypatch.setattr(audit_publish, 'PUSH_URL', str(remote))
    settings = {'enabled': True, 'ssh_key': str(tmp_path / 'unused-key')}
    commit = audit_publish.publish_report(report, settings)
    assert git('--git-dir', str(remote), 'show', 'main:outputs/strategy_review.md') == 'Reviewed the chip plan.'
    assert git('--git-dir', str(remote), 'show', 'main:source.txt') == 'newer source changes'
    assert git('--git-dir', str(remote), 'diff-tree', '--no-commit-id', '--name-only', '-r', commit) == 'outputs/strategy_review.md'
    assert (production / '.env').read_text() == 'private token'
    assert (production / 'unrelated.txt').read_text() == 'local edits'
    assert audit_publish.publish_report(report, settings) == 'unchanged'


def test_disabled_publication_does_not_read_report(tmp_path):
    assert audit_publish.publish_report(tmp_path / 'absent', {}) == 'disabled'
