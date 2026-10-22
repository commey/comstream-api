"""End-to-end API tests — all external calls are mocked."""

from __future__ import annotations

import httpx
import pytest
import respx

from tests.conftest import MOCK_MARKET_RESPONSE, MOCK_WEATHER_RESPONSE

pytestmark = pytest.mark.anyio


# ── Helpers ──────────────────────────────────────────────────────────────────

def _mock_external_apis() -> respx.MockRouter:
    """Return a respx router that intercepts Open-Meteo & CoinGecko calls."""
    mock = respx.mock(assert_all_called=False)
    mock.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(200, json=MOCK_WEATHER_RESPONSE),
    )
    mock.get("https://api.coingecko.com/api/v3/coins/markets").mock(
        return_value=httpx.Response(200, json=MOCK_MARKET_RESPONSE),
    )
    return mock


# ── Health ───────────────────────────────────────────────────────────────────

class TestHealth:
    """Tests for the /health endpoint."""

    async def test_health_returns_ok(self, client: httpx.AsyncClient) -> None:
        response = await client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "version" in body
        assert "timestamp" in body


# ── Dashboard ───────────────────────────────────────────────────────────────

class TestDashboard:
    """Tests for the /api/v1/dashboard/{city} endpoint."""

    async def test_dashboard_success(self, client: httpx.AsyncClient) -> None:
        """Happy-path: returns combined weather + market data."""
        with _mock_external_apis():
            response = await client.get("/api/v1/dashboard/london")

        assert response.status_code == 200
        body = response.json()

        # Weather assertions
        weather = body["weather"]
        assert weather["city"] == "London"
        assert weather["temperature_celsius"] == 18.5
        assert weather["wind_speed_kmh"] == 14.2
        assert weather["weather_code"] == 2

        # Market assertions
        market = body["market"]
        assert len(market["assets"]) == 2
        assert market["assets"][0]["symbol"] == "btc"
        assert market["assets"][1]["symbol"] == "eth"

        # Top-level
        assert "generated_at" in body

    async def test_dashboard_case_insensitive(
        self, client: httpx.AsyncClient
    ) -> None:
        """City lookup should be case-insensitive."""
        with _mock_external_apis():
            response = await client.get("/api/v1/dashboard/LONDON")
        assert response.status_code == 200
        assert response.json()["weather"]["city"] == "London"

    async def test_dashboard_unsupported_city(
        self, client: httpx.AsyncClient
    ) -> None:
        """Unknown city should return 400."""
        response = await client.get("/api/v1/dashboard/atlantis")
        assert response.status_code == 400
        assert "not supported" in response.json()["detail"].lower()

    async def test_dashboard_upstream_failure(
        self, client: httpx.AsyncClient
    ) -> None:
        """If an upstream API returns 500 repeatedly, we return 502."""
        mock = respx.mock(assert_all_called=False)
        mock.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(500, text="Internal Server Error"),
        )
        mock.get("https://api.coingecko.com/api/v3/coins/markets").mock(
            return_value=httpx.Response(200, json=MOCK_MARKET_RESPONSE),
        )
        with mock:
            response = await client.get("/api/v1/dashboard/london")
        assert response.status_code == 502


# ── Schema validation ──────────────────────────────────────────────────────

class TestSchemas:
    """Verify Pydantic schemas enforce types correctly."""

    async def test_weather_schema_validation(self) -> None:
        from app.schemas.dashboard import WeatherData

        with pytest.raises(Exception):
            # temperature_celsius expects a float, not a string
            WeatherData(
                city="Test",
                latitude=0.0,
                longitude=0.0,
                temperature_celsius="not_a_number",  # type: ignore[arg-type]
                wind_speed_kmh=0.0,
                weather_code=0,
                observation_time="2026-01-01T00:00:00",
            )

    async def test_crypto_asset_schema(self) -> None:
        from app.schemas.dashboard import CryptoAsset

        asset = CryptoAsset(
            id="bitcoin",
            symbol="btc",
            name="Bitcoin",
            current_price_usd=67000.0,
            market_cap_usd=1_300_000_000_000,
            price_change_24h_pct=1.5,
        )
        assert asset.symbol == "btc"
        assert asset.current_price_usd == 67000.0
