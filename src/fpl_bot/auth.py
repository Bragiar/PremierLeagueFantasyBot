from __future__ import annotations

import json
import os
import ctypes
import sys
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
    """Store credentials through the native macOS Keychain API."""

    _ITEM_NOT_FOUND = -25300

    def __init__(self) -> None:
        if sys.platform != "darwin":
            raise FPLAuthError("FPL credential storage requires macOS Keychain")
        self._security = ctypes.CDLL(
            "/System/Library/Frameworks/Security.framework/Security"
        )
        self._core_foundation = ctypes.CDLL(
            "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
        )
        self._configure_signatures()

    def _configure_signatures(self) -> None:
        self._security.SecKeychainFindGenericPassword.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_char_p,
            ctypes.c_uint32,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_void_p),
        ]
        self._security.SecKeychainFindGenericPassword.restype = ctypes.c_int32
        self._security.SecKeychainAddGenericPassword.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_char_p,
            ctypes.c_uint32,
            ctypes.c_char_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        self._security.SecKeychainAddGenericPassword.restype = ctypes.c_int32
        self._security.SecKeychainItemModifyAttributesAndData.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
        ]
        self._security.SecKeychainItemModifyAttributesAndData.restype = ctypes.c_int32
        self._security.SecKeychainItemFreeContent.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        self._security.SecKeychainItemFreeContent.restype = ctypes.c_int32
        self._core_foundation.CFRelease.argtypes = [ctypes.c_void_p]
        self._core_foundation.CFRelease.restype = None

    def _find_item(self, account: str) -> tuple[int, ctypes.c_void_p]:
        service = KEYCHAIN_SERVICE.encode("utf-8")
        account_bytes = account.encode("utf-8")
        item = ctypes.c_void_p()
        status = self._security.SecKeychainFindGenericPassword(
            None,
            len(service),
            service,
            len(account_bytes),
            account_bytes,
            None,
            None,
            ctypes.byref(item),
        )
        return status, item

    def get(self, account: str) -> str | None:
        service = KEYCHAIN_SERVICE.encode("utf-8")
        account_bytes = account.encode("utf-8")
        password_length = ctypes.c_uint32()
        password_data = ctypes.c_void_p()
        item = ctypes.c_void_p()
        status = self._security.SecKeychainFindGenericPassword(
            None,
            len(service),
            service,
            len(account_bytes),
            account_bytes,
            ctypes.byref(password_length),
            ctypes.byref(password_data),
            ctypes.byref(item),
        )
        if status == self._ITEM_NOT_FOUND:
            return None
        if status != 0:
            raise FPLAuthError("Could not read the FPL credential from macOS Keychain")
        try:
            value = ctypes.string_at(password_data, password_length.value).decode("utf-8")
            return value.strip() or None
        finally:
            self._security.SecKeychainItemFreeContent(None, password_data)
            if item:
                self._core_foundation.CFRelease(item)

    def set(self, account: str, value: str) -> None:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Cannot store an empty FPL credential")
        password = normalized.encode("utf-8")
        status, item = self._find_item(account)
        if status == 0:
            try:
                status = self._security.SecKeychainItemModifyAttributesAndData(
                    item,
                    None,
                    len(password),
                    password,
                )
            finally:
                self._core_foundation.CFRelease(item)
        elif status == self._ITEM_NOT_FOUND:
            service = KEYCHAIN_SERVICE.encode("utf-8")
            account_bytes = account.encode("utf-8")
            status = self._security.SecKeychainAddGenericPassword(
                None,
                len(service),
                service,
                len(account_bytes),
                account_bytes,
                len(password),
                password,
                None,
            )
        if status != 0:
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
    return normalize_refresh_token(token)


def normalize_refresh_token(value: str) -> str:
    """Accept a bare token, a JSON string, or the full oidc-client user object."""
    candidate: Any = value.strip()
    if not candidate:
        raise FPLAuthError("FPL refresh token is empty")
    if candidate.startswith("{") or (
        candidate.startswith('"') and candidate.endswith('"')
    ):
        try:
            decoded = json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise FPLAuthError("FPL refresh token contains invalid JSON") from exc
        candidate = decoded.get("refresh_token") if isinstance(decoded, dict) else decoded
    if not isinstance(candidate, str) or not candidate.strip():
        raise FPLAuthError("OIDC data does not contain a refresh_token value")
    candidate = candidate.strip()
    if candidate.lower().startswith("bearer "):
        candidate = candidate[7:].strip()
    if any(character.isspace() for character in candidate):
        raise FPLAuthError("FPL refresh token contains unexpected whitespace")
    return candidate


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
