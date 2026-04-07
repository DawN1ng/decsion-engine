# crypto_decision_engine

A read-only crypto decision engine MVP that ingests public market + derivatives + onchain-labeled flow + DEX liquidity data for configured assets and outputs deterministic directional actions.

## What it does
- Ingests Binance spot market, derived CEX flow, Bybit derivatives, GeckoTerminal liquidity, and config-driven onchain labeled wallet flow.
- Computes factor groups: CEX netflow, whale/team behavior, OI/funding, and liquidity/execution.
- Produces `long_score`, `short_score`, `risk_score`, `exec_score` and actions (`IGNORE`, `WATCH`, `PROBE_LONG`, `BUILD_LONG`, `REDUCE`, `REDUCE_OR_SHORT`, `EXIT`).
- Emits de-duplicated alerts with cooldown windows.

## What it does NOT do
- No order placement.
- No portfolio execution.
- No ML prediction.

## Local setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
docker compose up -d db redis
alembic upgrade head
python scripts/seed_assets.py
```

## Run API
```bash
uvicorn app.main:app --reload
```

## Run scheduler worker
```bash
python -m app.jobs.worker
```

## API endpoints
- `GET /health`
- `GET /assets`
- `GET /snapshots/{symbol}`
- `GET /factors/{symbol}`
- `GET /signals/{symbol}`
- `GET /alerts`

## Config files
- `configs/assets.yaml` watchlist + category metadata.
- `configs/wallet_labels.yaml` wallet labels.
- `configs/onchain_flows.json` manual labeled movement feed for MVP.
- `configs/factor_weights.yaml` per-category score weights.
- `configs/score_thresholds.yaml` per-category thresholds.
- `configs/scheduler.yaml` polling intervals + alert cooldown.

## Test
```bash
pytest -q
```
