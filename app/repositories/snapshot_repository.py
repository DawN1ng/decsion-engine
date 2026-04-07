from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.entities import (
    Alert,
    DerivativesSnapshot,
    FactorScore,
    LiquiditySnapshot,
    MarketSnapshot,
    OnchainFlow,
    Signal,
)


class SnapshotRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, obj: object) -> None:
        self.session.add(obj)
        await self.session.commit()

    async def latest_market(self, symbol: str) -> MarketSnapshot | None:
        q = select(MarketSnapshot).where(MarketSnapshot.asset_symbol == symbol).order_by(MarketSnapshot.ts.desc()).limit(1)
        return (await self.session.execute(q)).scalars().first()

    async def latest_onchain(self, symbol: str) -> OnchainFlow | None:
        q = select(OnchainFlow).where(OnchainFlow.asset_symbol == symbol).order_by(OnchainFlow.ts.desc()).limit(1)
        return (await self.session.execute(q)).scalars().first()

    async def latest_derivatives(self, symbol: str) -> DerivativesSnapshot | None:
        q = select(DerivativesSnapshot).where(DerivativesSnapshot.asset_symbol == symbol).order_by(DerivativesSnapshot.ts.desc()).limit(1)
        return (await self.session.execute(q)).scalars().first()

    async def latest_liquidity(self, symbol: str) -> LiquiditySnapshot | None:
        q = select(LiquiditySnapshot).where(LiquiditySnapshot.asset_symbol == symbol).order_by(LiquiditySnapshot.ts.desc()).limit(1)
        return (await self.session.execute(q)).scalars().first()

    async def latest_factor(self, symbol: str) -> FactorScore | None:
        q = select(FactorScore).where(FactorScore.asset_symbol == symbol).order_by(FactorScore.ts.desc()).limit(1)
        return (await self.session.execute(q)).scalars().first()

    async def latest_signal(self, symbol: str) -> Signal | None:
        q = select(Signal).where(Signal.asset_symbol == symbol).order_by(Signal.ts.desc()).limit(1)
        return (await self.session.execute(q)).scalars().first()

    async def list_alerts(self, limit: int = 50) -> list[Alert]:
        q = select(Alert).order_by(Alert.ts.desc()).limit(limit)
        return list((await self.session.execute(q)).scalars().all())
