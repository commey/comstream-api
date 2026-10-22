"""Shared pytest fixtures and mock data for the test suite."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


# ── Async test client ────────────────────────────────────────────────────────

@pytest.fixture
async def client() -> AsyncClient:
    """Yield an httpx AsyncClient wired to the FastAPI ASGI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Mock payloads ────────────────────────────────────────────────────────────

MOCK_WEATHER_RESPONSE: dict = {
    "current_weather": {
        "temperature": 18.5,
        "windspeed": 14.2,
        "weathercode": 2,
        "time": "2026-10-22T12:00",
    },
    "latitude": 51.5074,
    "longitude": -0.1278,
}

MOCK_MARKET_RESPONSE: list[dict] = [
    {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": 67234.0,
        "market_cap": 1_320_000_000_000,
        "price_change_percentage_24h": 2.34,
    },
    {
        "id": "ethereum",
        "symbol": "eth",
        "name": "Ethereum",
        "current_price": 3456.78,
        "market_cap": 415_000_000_000,
        "price_change_percentage_24h": -1.05,
    },
]
