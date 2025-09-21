from __future__ import annotations

from typing import Annotated, TypeAlias

from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.domain.services import CatFactProvider
from app.infrastructure.http.interfaces import HttpClient
from app.infrastructure.http.http_client import HttpxHttpClient
from app.infrastructure.providers.cat_fact_http_provider import CatFactHttpProvider


# Providers

def provide_settings() -> Settings:
    return get_settings()


SettingsDep: TypeAlias = Annotated[Settings, Depends(provide_settings)]


def provide_http_client(settings: SettingsDep) -> HttpClient:
    return HttpxHttpClient(settings=settings)


HttpClientDep: TypeAlias = Annotated[HttpClient, Depends(provide_http_client)]


def provide_cat_fact_provider(
    settings: SettingsDep,
    http: HttpClientDep,
) -> CatFactProvider:
    return CatFactHttpProvider(http=http, settings=settings)

CatFactProviderDep: TypeAlias = Annotated[CatFactProvider, Depends(provide_cat_fact_provider)]
