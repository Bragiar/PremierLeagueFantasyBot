from __future__ import annotations

from subprocess import CompletedProcess

import fpl_bot.cli as cli


def test_read_clipboard_secret_reads_then_clears(monkeypatch):
    calls: list[tuple[list[str], str | None]] = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs.get("input")))
        if command == ["pbpaste"]:
            return CompletedProcess(command, 0, '{"refresh_token":"secret"}', "")
        return CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    assert cli.read_clipboard_secret() == '{"refresh_token":"secret"}'
    assert calls == [(["pbpaste"], None), (["pbcopy"], "")]
