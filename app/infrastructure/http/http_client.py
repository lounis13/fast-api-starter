from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.config.settings import Settings
from app.infrastructure.http.interfaces import HttpClient


@dataclass(slots=True)
class HttpxHttpClient(HttpClient):
    settings: Settings

    async def get_json(self, url: str, *, headers: dict | None = None, params: dict | None = None) -> dict:
        timeout = httpx.Timeout(self.settings.http_timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
            return data
