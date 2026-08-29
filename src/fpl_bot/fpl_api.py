from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any


class FPLAPIError(RuntimeError):
    """Raised when official FPL data cannot be retrieved safely."""


class FPLClient:
    def __init__(self, base_url: str, timeout_seconds: int = 20, retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.retries = max(1, retries)

    def _get(self, path: str) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "fpl-recommendation-bot/0.1 (read-only)"},
        )
        last_error: Exception | None = None
        for attempt in range(self.retries):
            try:
                with urllib.request.urlopen(
                    request, timeout=self.timeout_seconds
                ) as response:
                    if response.status != 200:
                        raise FPLAPIError(f"FPL API returned HTTP {response.status}")
                    return json.load(response)
            except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt + 1 < self.retries:
                    time.sleep(0.5 * (attempt + 1))
        raise FPLAPIError(f"Could not fetch official FPL data: {last_error}")

    def bootstrap(self) -> dict[str, Any]:
        data = self._get("bootstrap-static/")
        required = {"elements", "teams", "events", "element_types"}
        if not isinstance(data, dict) or not required.issubset(data):
            raise FPLAPIError("FPL bootstrap response is missing required fields")
        return data

    def fixtures(self) -> list[dict[str, Any]]:
        data = self._get("fixtures/")
        if not isinstance(data, list):
            raise FPLAPIError("FPL fixtures response is not a list")
        return data

    def event_live(self, event_id: int) -> dict[str, Any]:
        data = self._get(f"event/{int(event_id)}/live/")
        if not isinstance(data, dict) or not isinstance(data.get("elements"), list):
            raise FPLAPIError("FPL live-event response is missing player data")
        return data
