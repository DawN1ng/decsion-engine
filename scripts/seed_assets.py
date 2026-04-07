import asyncio

from sqlalchemy import delete, insert

from app.core.config import get_settings
from app.db.session import engine
from app.domain.models.entities import Asset


async def main() -> None:
    settings = get_settings()
    assets = settings.load_yaml("assets.yaml").get("assets", [])
    async with engine.begin() as conn:
        await conn.execute(delete(Asset))
        if assets:
            await conn.execute(insert(Asset).values(assets))


if __name__ == "__main__":
    asyncio.run(main())
