from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.entities import Asset


class AssetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_assets(self) -> list[Asset]:
        res = await self.session.execute(select(Asset).where(Asset.is_active.is_(True)))
        return list(res.scalars().all())
