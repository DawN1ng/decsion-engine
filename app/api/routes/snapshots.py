from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.domain.schemas.common import MarketSnapshotSchema
from app.repositories.snapshot_repository import SnapshotRepository

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


@router.get("/{symbol}", response_model=MarketSnapshotSchema)
async def get_snapshot(symbol: str, session: AsyncSession = Depends(get_db_session)) -> MarketSnapshotSchema:
    snapshot = await SnapshotRepository(session).latest_market(symbol.upper())
    if not snapshot:
        raise HTTPException(status_code=404, detail="snapshot not found")
    return MarketSnapshotSchema.model_validate(snapshot)
