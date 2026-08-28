import io
import urllib.error
import urllib.request

import pytest

from fpl_bot.telegram import TelegramError, send_telegram


def test_telegram_http_error_preserves_safe_api_description(monkeypatch):
    error = urllib.error.HTTPError(
        "https://api.telegram.org/redacted/sendMessage",
        400,
        "Bad Request",
        {},
        io.BytesIO(b'{"ok":false,"description":"Bad Request: chat not found"}'),
    )

    def fail(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(urllib.request, "urlopen", fail)

    with pytest.raises(TelegramError, match="chat not found"):
        send_telegram("token", "chat", "message")
