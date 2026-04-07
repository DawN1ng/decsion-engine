from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.domain.schemas.common import FactorScoreSchema
from app.repositories.snapshot_repository import SnapshotRepository

router = APIRouter(prefix="/factors", tags=["factors"])


@router.get("/{symbol}", response_model=FactorScoreSchema)
async def get_factor(symbol: str, session: AsyncSession = Depends(get_db_session)) -> FactorScoreSchema:
    factor = await SnapshotRepository(session).latest_factor(symbol.upper())
    if not factor:
        raise HTTPException(status_code=404, detail="factor not found")
    return FactorScoreSchema.model_validate(factor)
