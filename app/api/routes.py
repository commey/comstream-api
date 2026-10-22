"""API route definitions."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas.dashboard import (
    DashboardResponse,
    ErrorResponse,
    HealthResponse,
)
from app.services.external_api import fetch_market, fetch_weather

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Health ───────────────────────────────────────────────────────────────────

@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Application health check",
)
async def health() -> HealthResponse:
    """Return the current health status of the API."""
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        timestamp=datetime.now(tz=timezone.utc),
    )


# ── Dashboard ───────────────────────────────────────────────────────────────

@router.get(
    "/api/v1/dashboard/{city}",
    response_model=DashboardResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Unsupported city"},
        502: {"model": ErrorResponse, "description": "Upstream API failure"},
    },
    tags=["dashboard"],
    summary="Aggregated weather + market dashboard",
)
async def dashboard(city: str) -> DashboardResponse:
    """Fetch weather and market data concurrently, return a unified response.

    - **city** – one of the supported city names (case-insensitive).
    """
    async with httpx.AsyncClient() as client:
        try:
            weather, market = await asyncio.gather(
                fetch_weather(client, city),
                fetch_market(client),
            )
        except ValueError as exc:
            # Unsupported city
            logger.warning("Bad request: %s", exc)
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except httpx.HTTPError as exc:
            logger.error("Upstream API error: %s", exc)
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch data from upstream API: {exc}",
            ) from exc

    return DashboardResponse(
        weather=weather,
        market=market,
        generated_at=datetime.now(tz=timezone.utc),
    )
