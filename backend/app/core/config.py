from __future__ import annotations

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "production"
    app_name: str = "AutoVIN Intelligence System"
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str
    redis_url: str

    cors_origins: str = "http://localhost:5173,http://frontend:80"
    rate_limit: str = "30/minute"

    nhtsa_base_url: AnyHttpUrl = "https://vpic.nhtsa.dot.gov/api/vehicles"
    vindecoder_api_base: AnyHttpUrl = "https://api.vindecoder.eu/3.2"
    vindecoder_api_key: str = ""

    cache_ttl_seconds: int = 60 * 60 * 24  # 24h


settings = Settings()
