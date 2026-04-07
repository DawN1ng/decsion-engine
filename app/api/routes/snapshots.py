from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.domain.schemas.common import (
    CexFlowSchema,
    DerivativesSnapshotSchema,
    LiquiditySnapshotSchema,
    MarketSnapshotSchema,
    OnchainFlowSchema,
    SnapshotBundleSchema,
)
from app.repositories.snapshot_repository import SnapshotRepository

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


@router.get("/{symbol}", response_model=SnapshotBundleSchema)
async def get_snapshot_bundle(symbol: str, session: AsyncSession = Depends(get_db_session)) -> SnapshotBundleSchema:
    repo = SnapshotRepository(session)
    symbol = symbol.upper()
    market = await repo.latest_market(symbol)
    cex_flow = await repo.latest_cex_flow(symbol)
    onchain = await repo.latest_onchain(symbol)
    derivatives = await repo.latest_derivatives(symbol)
    liquidity = await repo.latest_liquidity(symbol)
    return SnapshotBundleSchema(
        symbol=symbol,
        market=MarketSnapshotSchema.model_validate(market) if market else None,
        cex_flow=CexFlowSchema.model_validate(cex_flow) if cex_flow else None,
        onchain=OnchainFlowSchema.model_validate(onchain) if onchain else None,
        derivatives=DerivativesSnapshotSchema.model_validate(derivatives) if derivatives else None,
        liquidity=LiquiditySnapshotSchema.model_validate(liquidity) if liquidity else None,
    )
