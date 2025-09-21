import asyncio
import pytest

from app.application.use_cases import get_random_fact
from app.domain.entities import Fact
from app.domain.services import CatFactProvider


class FakeProvider(CatFactProvider):
    async def get_random_fact(self) -> Fact:
        await asyncio.sleep(0)
        return Fact(text="Cats have five toes on their front paws.", source="fake")


@pytest.mark.asyncio
async def test_get_random_fact_use_case_returns_fact():
    fact = await get_random_fact(provider=FakeProvider())
    assert isinstance(fact, Fact)
    assert fact.text
    assert fact.source == "fake"
