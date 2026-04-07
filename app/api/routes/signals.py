from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.domain.schemas.common import SignalSchema
from app.repositories.snapshot_repository import SnapshotRepository

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("/{symbol}", response_model=SignalSchema)
async def get_signal(symbol: str, session: AsyncSession = Depends(get_db_session)) -> SignalSchema:
    signal = await SnapshotRepository(session).latest_signal(symbol.upper())
    if not signal:
        raise HTTPException(status_code=404, detail="signal not found")
    return SignalSchema.model_validate(signal)
