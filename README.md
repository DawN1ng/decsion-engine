# crypto_decision_engine

Read-only crypto decision engine MVP built with FastAPI, SQLAlchemy 2.x, PostgreSQL, Redis, APScheduler, and Alembic.

## Features
- Config-driven watchlist assets, weights, thresholds, and wallet labels.
- Deterministic factor and scoring pipeline.
- Async provider clients with timeout/retry/rate-limit guards.
- Repository-based DB access and REST endpoints.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
docker compose up -d db redis
alembic upgrade head
uvicorn app.main:app --reload
```

## API
- `GET /health`
- `GET /assets`
- `GET /snapshots/{symbol}`
- `GET /factors/{symbol}`
- `GET /signals/{symbol}`
- `GET /alerts`

## Tests
```bash
pytest -q
```
