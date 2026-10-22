"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration sourced from env vars / .env file."""

    app_name: str = "ComStream API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Open-Meteo (free, no key required)
    open_meteo_base_url: str = "https://api.open-meteo.com/v1"

    # CoinGecko (free tier, no key required)
    coingecko_base_url: str = "https://api.coingecko.com/api/v3"

    # HTTP client settings
    http_timeout: float = 10.0
    max_retries: int = 3
    backoff_base: float = 0.5  # seconds

    model_config = {"env_prefix": "COMSTREAM_", "env_file": ".env"}


settings = Settings()
