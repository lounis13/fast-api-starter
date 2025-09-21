from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(StrEnum):
    local = "local"
    cloud = "cloud"
    gcp = "gcp"
    aws = "aws"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", ".env.local"), env_prefix="APP_", extra="ignore")

    # General
    name: str = Field(default="FastAPI Clean Starter")
    version: str = Field(default="0.1.0")
    env: AppEnv = Field(default=AppEnv.local)
    debug: bool = Field(default=True)
    log_level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = Field(default="INFO")

    # External APIs
    cat_fact_base_url: str = Field(default="https://catfact.ninja")
    http_timeout_seconds: float = Field(default=10.0)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
