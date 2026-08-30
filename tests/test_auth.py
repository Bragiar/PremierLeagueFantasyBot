from __future__ import annotations

import io
import json
import urllib.error

import pytest

from fpl_bot.auth import FPLAuthError, refresh_access_token


class FakeResponse:
    def __init__(self, value: dict[str, object]):
        self._body = io.BytesIO(json.dumps(value).encode())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self, *args):
        return self._body.read(*args)


def test_refresh_access_token_returns_rotated_refresh_token():
    def opener(request, timeout):
        assert request.full_url.endswith("/as/token")
        assert timeout == 30
        return FakeResponse(
            {"access_token": "access-value", "refresh_token": "rotated-value"}
        )

    tokens = refresh_access_token("original-value", opener=opener)

    assert tokens.access_token == "access-value"
    assert tokens.refresh_token == "rotated-value"


def test_refresh_access_token_reports_safe_oauth_error():
    def opener(request, timeout):
        raise urllib.error.HTTPError(
            request.full_url,
            400,
            "Bad Request",
            {},
            io.BytesIO(
                json.dumps(
                    {"error": "invalid_grant", "error_description": "Token expired"}
                ).encode()
            ),
        )

    with pytest.raises(FPLAuthError, match="Token expired"):
        refresh_access_token("expired-value", opener=opener)
