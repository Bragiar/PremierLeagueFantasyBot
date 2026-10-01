import json
import os

import pytest

from fpl_bot.fpl_api import FPLAPIError, FPLClient


def test_official_snapshot_requires_fresh_data(tmp_path, monkeypatch):
    snapshot = tmp_path / "bootstrap-static.json"
    snapshot.write_text(json.dumps({"elements": [], "teams": [], "events": [], "element_types": []}))
    monkeypatch.setenv("FPL_SNAPSHOT_DIR", str(tmp_path))
    client = FPLClient("https://fantasy.premierleague.com/api")

    assert client.bootstrap()["elements"] == []

    os.utime(snapshot, (1, 1))
    with pytest.raises(FPLAPIError, match="stale"):
        client.bootstrap()
