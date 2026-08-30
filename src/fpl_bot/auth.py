from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable


TOKEN_URL = "https://account.premierleague.com/as/token"
CLIENT_ID = "bfcbaf69-aade-4c1b-8f00-c1cb8a193030"
REDIRECT_URI = "https://fantasy.premierleague.com/"
KEYCHAIN_SERVICE = "com.bragiarnarson.fpl-recommendation-bot"
REFRESH_TOKEN_ACCOUNT = "fpl-refresh-token"
ENTRY_ID_ACCOUNT = "fpl-entry-id"


class FPLAuthError(RuntimeError):
    """Raised when local credentials or FPL authentication are unavailable."""


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str


class KeychainStore:
    """Small wrapper around the macOS Keychain command-line interface."""

    def get(self, account: str) -> str | None:
        result = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-s",
                KEYCHAIN_SERVICE,
                "-a",
                account,
                "-w",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip() or None

    def set(self, account: str, value: str) -> None:
        if not value.strip():
            raise ValueError("Cannot store an empty FPL credential")
        result = subprocess.run(
            [
                "security",
                "add-generic-password",
                "-U",
                "-s",
                KEYCHAIN_SERVICE,
                "-a",
                account,
                "-w",
            ],
            check=False,
            capture_output=True,
            text=True,
            input=value.strip() + "\n",
        )
        if result.returncode != 0:
            raise FPLAuthError("Could not save the FPL credential in macOS Keychain")


def stored_entry_id(store: KeychainStore) -> int:
    raw = store.get(ENTRY_ID_ACCOUNT) or os.getenv("FPL_ENTRY_ID", "").strip()
    try:
        entry_id = int(raw)
    except (TypeError, ValueError) as exc:
        raise FPLAuthError(
            "FPL entry ID is not configured; run `fpl-bot setup-fpl-auth`"
        ) from exc
    if entry_id <= 0:
        raise FPLAuthError("FPL entry ID must be a positive number")
    return entry_id


def stored_refresh_token(store: KeychainStore) -> str:
    token = store.get(REFRESH_TOKEN_ACCOUNT) or os.getenv(
        "FPL_REFRESH_TOKEN", ""
    ).strip()
    if not token:
        raise FPLAuthError(
            "FPL refresh token is not configured; run `fpl-bot setup-fpl-auth`"
        )
    return token


def _safe_error_description(payload: bytes) -> str:
    try:
        value = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return "authentication request was rejected"
    if not isinstance(value, dict):
        return "authentication request was rejected"
    description = value.get("error_description") or value.get("error")
    return str(description or "authentication request was rejected")[:300]


def refresh_access_token(
    refresh_token: str,
    *,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> TokenPair:
    body = urllib.parse.urlencode(
        {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": refresh_token,
            "redirect_uri": REDIRECT_URI,
            "scope": "openid profile email offline_access",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        TOKEN_URL,
        data=body,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "fpl-recommendation-bot/0.1 (local read-only sync)",
        },
    )
    try:
        with opener(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        description = _safe_error_description(exc.read())
        raise FPLAuthError(f"FPL sign-in refresh failed: {description}") from exc
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise FPLAuthError("Could not refresh the FPL sign-in") from exc

    if not isinstance(payload, dict) or not payload.get("access_token"):
        raise FPLAuthError("FPL token response did not include an access token")
    rotated = str(payload.get("refresh_token") or refresh_token).strip()
    return TokenPair(access_token=str(payload["access_token"]), refresh_token=rotated)


def authenticated_get(
    url: str,
    access_token: str,
    *,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Origin": "https://fantasy.premierleague.com",
            "Referer": "https://fantasy.premierleague.com/",
            "User-Agent": "fpl-recommendation-bot/0.1 (local read-only sync)",
            "X-Api-Authorization": f"Bearer {access_token}",
        },
    )
    try:
        with opener(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code in {401, 403}:
            raise FPLAuthError(
                "FPL rejected the authenticated team request; authorization must be renewed"
            ) from exc
        raise FPLAuthError(f"FPL team request returned HTTP {exc.code}") from exc
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise FPLAuthError("Could not retrieve the authenticated FPL team") from exc
