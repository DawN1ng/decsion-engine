from fastapi import FastAPI

from app.api.routes.alerts import router as alerts_router
from app.api.routes.assets import router as assets_router
from app.api.routes.factors import router as factors_router
from app.api.routes.health import router as health_router
from app.api.routes.signals import router as signals_router
from app.api.routes.snapshots import router as snapshots_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.jobs.scheduler import build_scheduler

configure_logging()

app = FastAPI(title="crypto_decision_engine")
app.include_router(health_router)
app.include_router(assets_router)
app.include_router(snapshots_router)
app.include_router(factors_router)
app.include_router(signals_router)
app.include_router(alerts_router)


@app.on_event("startup")
async def startup() -> None:
    if get_settings().scheduler_enabled:
        scheduler = build_scheduler()
        scheduler.start()
        app.state.scheduler = scheduler


@app.on_event("shutdown")
async def shutdown() -> None:
    scheduler = getattr(app.state, "scheduler", None)
    if scheduler:
        scheduler.shutdown()
