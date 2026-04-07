from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.domain.schemas.common import SignalSchema
from app.domain.services.data_quality_service import DataQualityService
from app.repositories.snapshot_repository import SnapshotRepository

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("/{symbol}", response_model=SignalSchema)
async def get_signal(symbol: str, session: AsyncSession = Depends(get_db_session)) -> SignalSchema:
    repo = SnapshotRepository(session)
    symbol = symbol.upper()
    signal = await repo.latest_signal(symbol)
    if not signal:
        raise HTTPException(status_code=404, detail="signal not found")
    market = await repo.latest_market(symbol)
    cex_flow = await repo.latest_cex_flow(symbol)
    onchain = await repo.latest_onchain(symbol)
    derivatives = await repo.latest_derivatives(symbol)
    liquidity = await repo.latest_liquidity(symbol)
    trust = DataQualityService().summarize(market, cex_flow, onchain, derivatives, liquidity)
    payload = SignalSchema.model_validate(signal).model_dump()
    payload["source_trust"] = trust
    return SignalSchema(**payload)
