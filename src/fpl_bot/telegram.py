from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


class TelegramError(RuntimeError):
    pass


def send_telegram(token: str, chat_id: str, message: str, timeout: int = 20) -> None:
    if not token or not chat_id:
        raise TelegramError("Telegram credentials are not configured")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise TelegramError("Telegram delivery failed") from exc
    if not payload.get("ok"):
        raise TelegramError("Telegram rejected the notification")
