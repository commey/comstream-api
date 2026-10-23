"""Pydantic v2 schemas for the dashboard endpoint."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


# ── Weather ──────────────────────────────────────────────────────────────────

class WeatherData(BaseModel):
    """Normalized weather snapshot for a city."""

    city: str = Field(..., examples=["London"])
    latitude: float = Field(..., examples=[51.5074])
    longitude: float = Field(..., examples=[-0.1278])
    temperature_celsius: float = Field(..., examples=[15.2])
    wind_speed_kmh: float = Field(..., examples=[12.5])
    weather_code: int = Field(
        ...,
        description="WMO weather interpretation code",
        examples=[3],
    )
    observation_time: datetime = Field(
        ...,
        description="ISO-8601 timestamp of the observation",
    )


# ── Market / Crypto ─────────────────────────────────────────────────────────

class CryptoAsset(BaseModel):
    """Snapshot of a single cryptocurrency."""

    id: str = Field(..., examples=["bitcoin"])
    symbol: str = Field(..., examples=["btc"])
    name: str = Field(..., examples=["Bitcoin"])
    current_price_usd: float = Field(..., examples=[67234.0])
    market_cap_usd: float = Field(..., examples=[1_320_000_000_000])
    price_change_24h_pct: float = Field(..., examples=[2.34])


class MarketData(BaseModel):
    """Aggregated crypto market data."""

    assets: list[CryptoAsset] = Field(
        default_factory=list,
        description="Top crypto assets by market cap",
    )
    retrieved_at: datetime


# ── Operational Correlation ──────────────────────────────────────────────────

class OperationalImpact(BaseModel):
    """Correlation indicators bridging meteorological conditions and digital asset operations."""

    cooling_demand: str = Field(
        ...,
        description="Facility cooling overhead for compute/mining hardware (low, moderate, high)",
        examples=["moderate"],
    )
    grid_stress_risk: str = Field(
        ...,
        description="Regional electricity grid strain risk driven by temperature extremes",
        examples=["low"],
    )
    curtailment_advisory: str = Field(
        ...,
        description="Operational and power curtailment advisory for mining infrastructure",
        examples=["Optimal thermodynamic efficiency; normal compute operations recommended."],
    )


# ── Dashboard (combined) ────────────────────────────────────────────────────

class DashboardResponse(BaseModel):
    """Unified response returned by the dashboard endpoint."""

    weather: WeatherData
    market: MarketData
    operational_impact: OperationalImpact
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ── Health ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Response schema for the health endpoint."""

    status: str = Field(..., examples=["ok"])
    version: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ── Errors ───────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Standard error envelope."""

    detail: str
