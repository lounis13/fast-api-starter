from __future__ import annotations

from fastapi.testclient import TestClient

from app.domain.entities import Fact
from app.domain.services import CatFactProvider
from app.main import app
from app.di.container import provide_cat_fact_provider


class FakeProvider(CatFactProvider):
    async def get_random_fact(self) -> Fact:
        return Fact(text="E2E fact", source="fake")


def test_get_random_fact_endpoint_returns_valid_payload():
    app.dependency_overrides[provide_cat_fact_provider] = lambda: FakeProvider()
    with TestClient(app) as client:
        res = client.get("/v1/facts/random")
        assert res.status_code == 200
        data = res.json()
        assert data["text"] == "E2E fact"
        assert data["source"] == "fake"
    app.dependency_overrides.clear()
