from __future__ import annotations

from dataclasses import dataclass

from app.config.settings import Settings
from app.domain.entities import Fact
from app.domain.services import CatFactProvider
from app.infrastructure.http.interfaces import HttpClient


@dataclass(slots=True)
class CatFactHttpProvider(CatFactProvider):
    http: HttpClient
    settings: Settings

    async def get_random_fact(self) -> Fact:
        url = f"{self.settings.cat_fact_base_url.rstrip('/')}/fact"
        data = await self.http.get_json(url)
        # catfact.ninja returns {"fact": str, "length": int}
        text = str(data.get("fact", ""))
        return Fact(text=text, source="catfact.ninja")
