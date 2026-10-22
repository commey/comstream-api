"""API route definitions."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import AsyncIterator

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from app.config import settings
from app.schemas.dashboard import (
    DashboardResponse,
    ErrorResponse,
    HealthResponse,
)
from app.services.external_api import fetch_market, fetch_weather

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Dependencies ─────────────────────────────────────────────────────────────

async def get_http_client(request: Request) -> AsyncIterator[httpx.AsyncClient]:
    """Provide a pooled HTTP client from app state with a per-request fallback."""
    client: httpx.AsyncClient | None = getattr(request.app.state, "http_client", None)
    if client is not None and not client.is_closed:
        yield client
    else:
        async with httpx.AsyncClient(timeout=settings.http_timeout) as temp_client:
            yield temp_client


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
async def dashboard(
    city: str,
    client: httpx.AsyncClient = Depends(get_http_client),
) -> DashboardResponse:
    """Fetch weather and market data concurrently, return a unified response.

    - **city** – one of the supported city names (case-insensitive).
    """
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
