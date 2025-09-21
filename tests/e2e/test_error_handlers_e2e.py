from __future__ import annotations

from fastapi.testclient import TestClient

from app.domain.entities import Fact
from app.domain.services import CatFactProvider
from app.main import app
from app.di.container import provide_cat_fact_provider


class ShortFactProvider(CatFactProvider):
    async def get_random_fact(self) -> Fact:
        return Fact(text="short", source="fake")


class ExplodingProvider(CatFactProvider):
    async def get_random_fact(self) -> Fact:
        raise RuntimeError("boom")


def test_validation_error_for_min_length_query_param():
    with TestClient(app) as client:
        res = client.get("/v1/facts/random", params={"min_length": 0})  # ge=1 violates
        assert res.status_code == 422
        data = res.json()
        assert data["error"] == "validation_error"
        assert data["message"] == "Validation error"
        assert isinstance(data.get("details"), dict)
        assert "errors" in data["details"]


def test_http_exception_formatted_for_min_length_not_satisfied():
    app.dependency_overrides[provide_cat_fact_provider] = lambda: ShortFactProvider()
    try:
        with TestClient(app) as client:
            res = client.get("/v1/facts/random", params={"min_length": 100})
            assert res.status_code == 404
            data = res.json()
            assert data["error"] == "not_found"
            assert "No fact satisfies" in data["message"]
    finally:
        app.dependency_overrides.clear()


def test_unhandled_exception_mapped_to_internal_error():
    app.dependency_overrides[provide_cat_fact_provider] = lambda: ExplodingProvider()
    try:
        with TestClient(app) as client:
            res = client.get("/v1/facts/random")
            assert res.status_code == 500
            data = res.json()
            assert data["error"] == "internal_error"
            assert data["message"] == "Internal Server Error"
            assert data.get("details") is None
    finally:
        app.dependency_overrides.clear()
