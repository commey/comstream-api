# 🌐 ComStream API

> **Async Weather & Market Data Aggregator** — A modern, production-ready Python API that concurrently fetches real-time meteorological telemetry and cryptocurrency market data, assesses regional power grid strain & facility thermodynamic cooling demand, and delivers a unified operational dashboard.

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#running-tests)

---

## 💡 Domain Motivation: Why Correlate Weather & Digital Assets?

In modern energy and computational infrastructure, **weather and digital asset operations are deeply interdependent**:

1. **Power Grid Stress & Peak Demand**:
   - Extreme heatwaves (>35°C) trigger regional air-conditioning peaks; winter freezes (< -5°C) drive massive heating spikes.
   - Grid operators (e.g. ERCOT in Texas, CAISO in California) experience severe supply stress during these anomalies.
2. **Industrial Mining Curtailment & Demand Response**:
   - Large-scale crypto mining data centers participate in automated demand-response programs, temporarily curtailing power draw during peak grid stress to stabilize municipal power reserves and avoid volatile spot power rates.
3. **Facility Thermodynamics & Economizer Cooling**:
   - Compute hardware requires intensive HVAC cooling. Ambient air temperature dictates whether facilities can use free-air convective cooling or must run energy-intensive chillers.

**ComStream API** bridges this gap: it correlates local environmental telemetry directly with asset market data to produce actionable operational risk and curtailment advisories.

---

## ✨ Features

- **Concurrent data fetching** — Weather + crypto market data retrieved in parallel via `asyncio.gather()`
- **Operational Intelligence Engine** — Computes thermodynamic cooling demand, regional grid stress risk, and curtailment advisories
- **Connection Pooling & Lifespan** — Persistent TCP/SSL connection reuse via FastAPI `lifespan` context manager
- **Exponential backoff retry** — Resilient HTTP client with configurable retry logic for upstream failures
- **Pydantic v2 validation** — Strict request/response schemas with automatic OpenAPI docs
- **Structured logging** — Human-readable, timestamped log output
- **100% offline test suite** — All external API calls mocked with `respx`
- **Clean architecture** — Analytics domain, service layer, route layer, and schema layer clearly separated

---

## 🏗️ Architecture

```
comstream-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application factory, lifespan & logging setup
│   ├── config.py             # Pydantic Settings (env-based configuration)
│   ├── schemas/
│   │   └── dashboard.py      # Pydantic v2 models (WeatherData, MarketData, OperationalImpact)
│   ├── services/
│   │   ├── __init__.py        # Re-exports
│   │   ├── analytics.py      # Operational impact & grid risk calculation engine
│   │   └── external_api.py   # Async HTTP clients (Open-Meteo, CoinGecko) with backoff retry
│   └── api/
│       ├── __init__.py
│       └── routes.py         # Endpoint definitions & dependency injection
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Fixtures & mock payloads
│   └── test_api.py           # Full test suite (API endpoints & analytics unit tests)
├── requirements.txt
├── pyproject.toml
├── README.md
└── .gitignore
```

### Data Flow

```
Client Request
      │
      ▼
  /api/v1/dashboard/{city}
      │
      ├──── asyncio.gather() ────┐
      │                          │
      ▼                          ▼
  Open-Meteo API          CoinGecko API
  (weather telemetry)      (crypto market data)
      │                          │
      └─────────┬────────────────┘
                ▼
      assess_operational_impact()
      (cooling demand + grid risk)
                │
                ▼
        DashboardResponse
          (Pydantic v2)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- `pip` (or your preferred package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/commey/comstream-api.git
cd comstream-api

# Create and activate a virtual environment
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

- **Interactive docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📡 API Endpoints

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2026-10-22T12:00:00Z"
}
```

### `GET /api/v1/dashboard/{city}`

Aggregated weather and market dashboard.

**Supported cities:** Berlin, Dubai, London, New York, Paris, San Francisco, Singapore, Sydney, Tokyo, Toronto

**Example request:**
```bash
curl http://localhost:8000/api/v1/dashboard/london
```

**Example response:**
```json
{
  "weather": {
    "city": "London",
    "latitude": 51.5074,
    "longitude": -0.1278,
    "temperature_celsius": 15.2,
    "wind_speed_kmh": 12.5,
    "weather_code": 3,
    "observation_time": "2026-10-22T12:00:00"
  },
  "market": {
    "assets": [
      {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price_usd": 67234.0,
        "market_cap_usd": 1320000000000,
        "price_change_24h_pct": 2.34
      },
      {
        "id": "ethereum",
        "symbol": "eth",
        "name": "Ethereum",
        "current_price_usd": 3456.78,
        "market_cap_usd": 415000000000,
        "price_change_24h_pct": -1.05
      }
    ],
    "retrieved_at": "2026-10-22T12:00:00Z"
  },
  "operational_impact": {
    "cooling_demand": "low",
    "grid_stress_risk": "low",
    "curtailment_advisory": "Optimal thermodynamic efficiency. Natural convective cooling effective; normal compute operations recommended."
  },
  "generated_at": "2026-10-22T12:00:00Z"
}
```

**Error responses:**
| Status | Description |
|--------|-------------|
| `400`  | Unsupported city name |
| `502`  | Upstream API failure (after retries) |

---

## ⚙️ Configuration

All configuration is driven by environment variables (with sensible defaults). Prefix every variable with `COMSTREAM_`.

| Variable | Default | Description |
|----------|---------|-------------|
| `COMSTREAM_DEBUG` | `false` | Enable debug-level logging |
| `COMSTREAM_HTTP_TIMEOUT` | `10.0` | HTTP request timeout (seconds) |
| `COMSTREAM_MAX_RETRIES` | `3` | Max retry attempts for upstream calls |
| `COMSTREAM_BACKOFF_BASE` | `0.5` | Base delay for exponential backoff (seconds) |

You can also create a `.env` file in the project root:

```env
COMSTREAM_DEBUG=true
COMSTREAM_MAX_RETRIES=5
```

---

## 🧪 Running Tests

The test suite runs **fully offline** — all external API calls are mocked.

```bash
pytest -v
```

Expected output:
```
tests/test_api.py::TestHealth::test_health_returns_ok               PASSED
tests/test_api.py::TestDashboard::test_dashboard_success            PASSED
tests/test_api.py::TestDashboard::test_dashboard_case_insensitive     PASSED
tests/test_api.py::TestDashboard::test_dashboard_slug_city_name    PASSED
tests/test_api.py::TestDashboard::test_dashboard_unsupported_city    PASSED
tests/test_api.py::TestDashboard::test_dashboard_upstream_failure    PASSED
tests/test_api.py::TestSchemas::test_weather_schema_validation      PASSED
tests/test_api.py::TestSchemas::test_crypto_asset_schema            PASSED
tests/test_api.py::TestAnalytics::test_extreme_heat_assessment      PASSED
tests/test_api.py::TestAnalytics::test_freezing_assessment          PASSED
tests/test_api.py::TestAnalytics::test_moderate_warm_assessment      PASSED
tests/test_api.py::TestAnalytics::test_mild_optimal_assessment        PASSED
```

---

## 🔧 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **`asyncio.gather()`** for concurrency | Fetches weather + market data in parallel, cutting latency roughly in half |
| **Connection Pooling & Lifespan** | Reuses persistent TCP/SSL connections via FastAPI lifespan and dependency injection |
| **Exponential backoff** | Gracefully handles transient upstream failures without hammering APIs |
| **`respx`** for test mocking | Works natively with `httpx` — no monkeypatching required |
| **Pydantic v2 `BaseModel`** | Strict validation, automatic JSON schema, and excellent IDE support |
| **No API keys required** | Open-Meteo and CoinGecko free tiers keep the project zero-config |
| **Service/route separation** | Business logic is testable independently of HTTP transport |

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
