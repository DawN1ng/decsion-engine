from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.entities import (
    Alert,
    CexFlowSnapshot,
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

    async def insert(self, obj: object) -> None:
        self.session.add(obj)
        await self.session.commit()

    async def latest_market(self, symbol: str, venue: str | None = None) -> MarketSnapshot | None:
        q = select(MarketSnapshot).where(MarketSnapshot.asset_symbol == symbol)
        if venue:
            q = q.where(MarketSnapshot.venue == venue)
        return (await self.session.execute(q.order_by(MarketSnapshot.ts.desc()).limit(1))).scalars().first()

    async def latest_cex_flow(self, symbol: str, venue: str | None = None) -> CexFlowSnapshot | None:
        q = select(CexFlowSnapshot).where(CexFlowSnapshot.asset_symbol == symbol)
        if venue:
            q = q.where(CexFlowSnapshot.venue == venue)
        return (await self.session.execute(q.order_by(CexFlowSnapshot.ts.desc()).limit(1))).scalars().first()

    async def latest_onchain(self, symbol: str) -> OnchainFlow | None:
        q = select(OnchainFlow).where(OnchainFlow.asset_symbol == symbol)
        return (await self.session.execute(q.order_by(OnchainFlow.ts.desc()).limit(1))).scalars().first()

    async def latest_derivatives(self, symbol: str, venue: str | None = None) -> DerivativesSnapshot | None:
        q = select(DerivativesSnapshot).where(DerivativesSnapshot.asset_symbol == symbol)
        if venue:
            q = q.where(DerivativesSnapshot.venue == venue)
        return (await self.session.execute(q.order_by(DerivativesSnapshot.ts.desc()).limit(1))).scalars().first()

    async def latest_liquidity(self, symbol: str, venue: str | None = None) -> LiquiditySnapshot | None:
        q = select(LiquiditySnapshot).where(LiquiditySnapshot.asset_symbol == symbol)
        if venue:
            q = q.where(LiquiditySnapshot.venue == venue)
        return (await self.session.execute(q.order_by(LiquiditySnapshot.ts.desc()).limit(1))).scalars().first()

    async def latest_factor(self, symbol: str) -> FactorScore | None:
        q = select(FactorScore).where(FactorScore.asset_symbol == symbol)
        return (await self.session.execute(q.order_by(FactorScore.ts.desc()).limit(1))).scalars().first()

    async def latest_signal(self, symbol: str) -> Signal | None:
        q = select(Signal).where(Signal.asset_symbol == symbol)
        return (await self.session.execute(q.order_by(Signal.ts.desc()).limit(1))).scalars().first()

    async def list_alerts(self, limit: int = 50) -> list[Alert]:
        q = select(Alert).order_by(Alert.ts.desc()).limit(limit)
        return list((await self.session.execute(q)).scalars().all())

    async def alert_exists_recent(self, symbol: str, alert_type: str, cooldown_minutes: int) -> bool:
        since = datetime.now(timezone.utc) - timedelta(minutes=cooldown_minutes)
        q = select(Alert.id).where(
            and_(Alert.asset_symbol == symbol, Alert.alert_type == alert_type, Alert.ts >= since)
        )
        return (await self.session.execute(q.limit(1))).first() is not None
