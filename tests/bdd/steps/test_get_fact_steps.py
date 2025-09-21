from __future__ import annotations

from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, scenarios, then, when

from app.domain.entities import Fact
from app.domain.services import CatFactProvider
from app.di.container import provide_cat_fact_provider
from app.main import app

scenarios("../features/get_fact.feature")


class StubProvider(CatFactProvider):
    async def get_random_fact(self) -> Fact:
        return Fact(text="BDD fact", source="stub")


@pytest.fixture
def context() -> Dict[str, Any]:
    return {}


@given("the API is running")
def api_running():
    # Lifespan is handled by TestClient context manager in the step below
    pass


@given("the fact use case is stubbed to return a fixed value")
def stub_use_case():
    app.dependency_overrides[provide_cat_fact_provider] = lambda: StubProvider()


@when("I call GET /v1/facts/random")
def call_endpoint(context: Dict[str, Any]):
    with TestClient(app) as client:
        res = client.get("/v1/facts/random")
        context["response"] = res


@then("the response status should be 200")
def assert_status_ok(context: Dict[str, Any]):
    res = context.get("response")
    assert res is not None
    assert res.status_code == 200


@then("the response should contain the fixed fact")
def assert_payload(context: Dict[str, Any]):
    res = context.get("response")
    assert res is not None
    data = res.json()
    assert data["text"] == "BDD fact"
    assert data["source"] == "stub"
    app.dependency_overrides.clear()
