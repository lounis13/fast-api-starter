import pytest

from app.config.settings import Settings
from app.infrastructure.http.http_client import HttpxHttpClient


@pytest.mark.asyncio
async def test_httpx_http_client_gets_json_from_public_api():
    settings = Settings()
    client = HttpxHttpClient(settings=settings)
    data = await client.get_json(f"{settings.cat_fact_base_url}/fact")
    assert isinstance(data, dict)
    assert "fact" in data
