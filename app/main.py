"""ComStream API — Async Weather & Market Data Aggregator."""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging
import sys
from typing import AsyncIterator

import httpx
from fastapi import FastAPI

from app.api.routes import router
from app.config import settings


def _configure_logging() -> None:
    """Set up structured, human-readable logging to stdout."""
    log_level = logging.DEBUG if settings.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )


_configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle resources (e.g. shared HTTP client pool)."""
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
    async with httpx.AsyncClient(limits=limits, timeout=settings.http_timeout) as client:
        app.state.http_client = client
        yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Production-ready async API correlating real-time weather telemetry with "
        "cryptocurrency market data and grid impact for digital asset and mining operations."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(router)
