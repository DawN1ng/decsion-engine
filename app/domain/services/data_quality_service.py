from __future__ import annotations

from app.domain.models.entities import CexFlowSnapshot, DerivativesSnapshot, LiquiditySnapshot, MarketSnapshot, OnchainFlow


class DataQualityService:
    def summarize(
        self,
        market: MarketSnapshot | None,
        cex_flow: CexFlowSnapshot | None,
        onchain: OnchainFlow | None,
        derivatives: DerivativesSnapshot | None,
        liquidity: LiquiditySnapshot | None,
    ) -> dict:
        return {
            "market_data_present": market is not None,
            "derivatives_present": derivatives is not None,
            "onchain_present": onchain is not None,
            "liquidity_present": liquidity is not None,
            "cex_flow_trust_level": cex_flow.trust_level if cex_flow else "none",
        }
