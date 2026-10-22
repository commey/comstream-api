"""External API service layer — async HTTP calls with retry & backoff."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from app.config import settings
from app.schemas.dashboard import (
    CryptoAsset,
    MarketData,
    WeatherData,
)

logger = logging.getLogger(__name__)

# ── Geocoding lookup (city → lat/lon) ───────────────────────────────────────

CITY_COORDINATES: dict[str, tuple[float, float]] = {
    "london": (51.5074, -0.1278),
    "new york": (40.7128, -74.0060),
    "tokyo": (35.6762, 139.6503),
    "paris": (48.8566, 2.3522),
    "berlin": (52.5200, 13.4050),
    "sydney": (-33.8688, 151.2093),
    "san francisco": (37.7749, -122.4194),
    "toronto": (43.6532, -79.3832),
    "singapore": (1.3521, 103.8198),
    "dubai": (25.2048, 55.2708),
}


def _resolve_coordinates(city: str) -> tuple[float, float]:
    """Return (lat, lon) for a known city, or raise ValueError."""
    key = city.strip().lower()
    if key not in CITY_COORDINATES:
        supported = ", ".join(sorted(CITY_COORDINATES))
        raise ValueError(
            f"City '{city}' is not supported. "
            f"Supported cities: {supported}"
        )
    return CITY_COORDINATES[key]


# ── Retry helper ────────────────────────────────────────────────────────────

async def _request_with_retry(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    max_retries: int = settings.max_retries,
    backoff_base: float = settings.backoff_base,
) -> httpx.Response:
    """Execute an HTTP request with exponential-backoff retry.

    Retries on 5xx server errors and network-level failures.  Client
    errors (4xx) are raised immediately.
    """
    last_exc: Exception | None = None

    for attempt in range(max_retries):
        try:
            response = await client.request(
                method, url, params=params, timeout=settings.http_timeout
            )
            if response.status_code < 500:
                response.raise_for_status()
                return response

            # 5xx → retry
            logger.warning(
                "Attempt %d/%d for %s returned %d — retrying",
                attempt + 1,
                max_retries,
                url,
                response.status_code,
            )
        except httpx.HTTPStatusError:
            raise  # 4xx — don't retry
        except httpx.HTTPError as exc:
            logger.warning(
                "Attempt %d/%d for %s failed: %s — retrying",
                attempt + 1,
                max_retries,
                url,
                exc,
            )
            last_exc = exc

        # Exponential backoff: 0.5s, 1s, 2s, …
        delay = backoff_base * (2 ** attempt)
        await asyncio.sleep(delay)

    # Exhausted retries
    if last_exc:
        raise last_exc
    raise httpx.HTTPError(f"Request to {url} failed after {max_retries} retries")


# ── Weather service (Open-Meteo) ────────────────────────────────────────────

async def fetch_weather(client: httpx.AsyncClient, city: str) -> WeatherData:
    """Fetch current weather from the Open-Meteo API.

    Open-Meteo is free and requires no API key.
    """
    lat, lon = _resolve_coordinates(city)
    url = f"{settings.open_meteo_base_url}/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
    }

    logger.info("Fetching weather for %s (%.4f, %.4f)", city, lat, lon)
    response = await _request_with_retry(client, "GET", url, params=params)
    data = response.json()

    current = data["current_weather"]
    return WeatherData(
        city=city.title(),
        latitude=lat,
        longitude=lon,
        temperature_celsius=current["temperature"],
        wind_speed_kmh=current["windspeed"],
        weather_code=current["weathercode"],
        observation_time=datetime.fromisoformat(current["time"]),
    )


# ── Market service (CoinGecko) ──────────────────────────────────────────────

async def fetch_market(client: httpx.AsyncClient) -> MarketData:
    """Fetch top crypto assets from the CoinGecko free API."""
    url = f"{settings.coingecko_base_url}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 5,
        "page": 1,
        "sparkline": "false",
    }

    logger.info("Fetching market data from CoinGecko")
    response = await _request_with_retry(client, "GET", url, params=params)
    raw_assets: list[dict[str, Any]] = response.json()

    assets = [
        CryptoAsset(
            id=asset["id"],
            symbol=asset["symbol"],
            name=asset["name"],
            current_price_usd=asset["current_price"],
            market_cap_usd=asset["market_cap"],
            price_change_24h_pct=asset.get("price_change_percentage_24h", 0.0),
        )
        for asset in raw_assets
    ]

    return MarketData(
        assets=assets,
        retrieved_at=datetime.now(tz=timezone.utc),
    )
