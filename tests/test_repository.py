import pytest
pytest.importorskip("aiosqlite")
import asyncio
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.domain.models.entities import Asset, CexFlowSnapshot, MarketSnapshot
from app.repositories.snapshot_repository import SnapshotRepository


def test_repository_latest_with_venue_filter() -> None:
    async def run() -> None:
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        async with session_factory() as session:
            session.add(Asset(symbol="ETH", name="Ethereum", category="midcap_alt", chain="ethereum", token_address=None, quote_currency="USDT", is_active=True))
            await session.commit()

            session.add_all([
                MarketSnapshot(
                    asset_symbol="ETH", venue="binance", ts=datetime.now(timezone.utc), last_price=Decimal("100"), volume_24h=Decimal("1"),
                    bid_ask_spread_bps=Decimal("1"), orderbook_depth_usd_1pct=Decimal("1"), raw_payload={}
                ),
                CexFlowSnapshot(
                    asset_symbol="ETH", venue="binance", ts=datetime.now(timezone.utc), inflow_usd=Decimal("1"), outflow_usd=Decimal("2"),
                    netflow_usd=Decimal("1"), source_type="derived", trust_level="low", raw_payload={}
                ),
            ])
            await session.commit()
            repo = SnapshotRepository(session)
            market = await repo.latest_market("ETH", venue="binance")
            flow = await repo.latest_cex_flow("ETH", venue="binance")
            assert market is not None
            assert flow is not None

    asyncio.run(run())
