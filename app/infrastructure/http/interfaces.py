from __future__ import annotations

import abc


class HttpClient(abc.ABC):
    @abc.abstractmethod
    async def get_json(self, url: str, *, headers: dict | None = None, params: dict | None = None) -> dict:
        """Perform an HTTP GET and return the parsed JSON as a dict."""
        raise NotImplementedError
