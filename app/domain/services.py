from __future__ import annotations

from typing import Protocol

from .entities import Fact


class CatFactProvider(Protocol):
    async def get_random_fact(self) -> Fact:
        """Return a random fact from some external source."""
        ...


