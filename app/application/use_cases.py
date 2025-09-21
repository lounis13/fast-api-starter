from __future__ import annotations

from app.domain.entities import Fact
from app.di.container import CatFactProviderDep


async def get_random_fact(provider: CatFactProviderDep) -> Fact:
    """Return a random Fact using the provided CatFactProvider."""
    return await provider.get_random_fact()