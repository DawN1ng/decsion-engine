from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.domain.schemas.common import AlertSchema
from app.repositories.snapshot_repository import SnapshotRepository

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertSchema])
async def get_alerts(session: AsyncSession = Depends(get_db_session)) -> list[AlertSchema]:
    alerts = await SnapshotRepository(session).list_alerts()
    return [AlertSchema.model_validate(a) for a in alerts]
