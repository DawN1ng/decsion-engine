from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.entities import Asset


class AssetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_assets(self, active_only: bool = True) -> list[Asset]:
        q = select(Asset)
        if active_only:
            q = q.where(Asset.is_active.is_(True))
        res = await self.session.execute(q.order_by(Asset.symbol.asc()))
        return list(res.scalars().all())
