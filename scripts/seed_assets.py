import asyncio

from sqlalchemy import insert

from app.core.config import get_settings
from app.db.session import engine
from app.domain.models.entities import Asset


async def main() -> None:
    settings = get_settings()
    assets = settings.load_yaml("assets.yaml").get("assets", [])
    values = [{"symbol": a["symbol"], "name": a["name"], "is_active": True} for a in assets]
    async with engine.begin() as conn:
        if values:
            await conn.execute(insert(Asset).values(values))


if __name__ == "__main__":
    asyncio.run(main())
