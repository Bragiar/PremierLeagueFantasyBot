import shutil
from pathlib import Path

import yaml

from fpl_bot.config import load_strategy
from fpl_bot.fpl_api import FPLAPIError, FPLClient
from fpl_bot.service import run


def test_local_settings_override_only_selected_fields(tmp_path):
    path = tmp_path / 'strategy.yaml'
    base = {'strategy': {'horizon': 5}, 'notifications': {'offsets_minutes': [1440], 'tolerance_minutes': 40},
            'openai': {'enabled': False}, 'fpl_api': {'base_url': 'https://example.invalid'}}
    path.write_text(yaml.safe_dump(base))
    (tmp_path / 'strategy.local.yaml').write_text(yaml.safe_dump({'notifications': {'offsets_minutes': [120]}}))
    result = load_strategy(path)
    assert result['notifications'] == {'offsets_minutes': [120], 'tolerance_minutes': 40}
    assert yaml.safe_load(path.read_text()) == base


def test_preview_writes_to_runtime_without_overwriting_checkout(tmp_path, monkeypatch):
    repository = Path(__file__).resolve().parents[1]
    root, runtime = tmp_path / 'checkout', tmp_path / 'runtime'
    for name in ('config', 'data'):
        shutil.copytree(repository / name, root / name)
    (root / 'config/strategy.local.yaml').write_text(yaml.safe_dump({
        'runtime': {'directory': str(runtime)}, 'codex': {'enabled': False},
    }))
    def unavailable(_client):
        raise FPLAPIError('simulated outage')
    monkeypatch.setattr(FPLClient, 'bootstrap', unavailable)
    result = run(root, preview=True, force=True, disable_openai=True)
    assert result.status == 'preview'
    assert (runtime / 'outputs/latest_recommendation.md').exists()
    assert not (root / 'outputs').exists()
    assert not (runtime / 'state/last_run.json').exists()
