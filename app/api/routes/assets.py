from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.domain.schemas.common import AssetSchema
from app.repositories.asset_repository import AssetRepository

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetSchema])
async def list_assets(session: AsyncSession = Depends(get_db_session)) -> list[AssetSchema]:
    assets = await AssetRepository(session).list_assets()
    return [AssetSchema.model_validate(a) for a in assets]
