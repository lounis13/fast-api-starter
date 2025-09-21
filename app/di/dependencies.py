from __future__ import annotations

from typing import Annotated, TypeAlias

from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.domain.services import CatFactProvider
from app.infrastructure.http.interfaces import HttpClient
from app.infrastructure.http.http_client import HttpxHttpClient
from app.infrastructure.providers.cat_fact_http_provider import CatFactHttpProvider
from app.infrastructure.cache.interfaces import Cache
from app.infrastructure.cache.memory_cache import MemoryTTLCache
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.providers.cached_cat_fact_provider import (
    CachedCatFactProvider,
)


# Providers

def provide_settings() -> Settings:
    return get_settings()


SettingsDep: TypeAlias = Annotated[Settings, Depends(provide_settings)]


def provide_http_client(settings: SettingsDep) -> HttpClient:
    return HttpxHttpClient(settings=settings)


HttpClientDep: TypeAlias = Annotated[HttpClient, Depends(provide_http_client)]


def provide_cache(settings: SettingsDep) -> Cache | None:
    if not settings.cache_enabled:
        return None
    if settings.cache_backend == "redis" and settings.redis_url:
        try:
            return RedisCache(settings.redis_url)
        except Exception:
            # Fallback to memory if Redis not available
            return MemoryTTLCache(maxsize=settings.cache_memory_maxsize)
    # default: memory
    return MemoryTTLCache(maxsize=settings.cache_memory_maxsize)


CacheDep: TypeAlias = Annotated[Cache | None, Depends(provide_cache)]


def provide_cat_fact_provider(
    settings: SettingsDep,
    http: HttpClientDep,
    cache: CacheDep,
) -> CatFactProvider:
    base = CatFactHttpProvider(http=http, settings=settings)
    if settings.cache_enabled:
        return CachedCatFactProvider(underlying=base, cache=cache, ttl_seconds=settings.cache_ttl_seconds)
    return base


CatFactProviderDep: TypeAlias = Annotated[CatFactProvider, Depends(provide_cat_fact_provider)]
