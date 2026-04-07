from fastapi import FastAPI

from app.api.routes.alerts import router as alerts_router
from app.api.routes.assets import router as assets_router
from app.api.routes.factors import router as factors_router
from app.api.routes.health import router as health_router
from app.api.routes.signals import router as signals_router
from app.api.routes.snapshots import router as snapshots_router
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(title="crypto_decision_engine")
app.include_router(health_router)
app.include_router(assets_router)
app.include_router(snapshots_router)
app.include_router(factors_router)
app.include_router(signals_router)
app.include_router(alerts_router)
