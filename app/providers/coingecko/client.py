from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.providers.base import ProviderClient


class CoinGeckoOnchainClient(ProviderClient):
    base_url = "https://api.geckoterminal.com/api/v2"

    async def fetch(self, symbol: str, chain: str = "eth", **kwargs: Any) -> dict[str, Any]:
        # Uses first matching pool for token symbol as MVP heuristic.
        search = await self.http.get(f"{self.base_url}/search/pools", params={"query": symbol.upper()})
        pools = search.get("data", [])
        if not pools:
            return {
                "asset_symbol": symbol.upper(),
                "venue": "geckoterminal",
                "venue_type": "dex",
                "chain": chain,
                "pool_id": None,
                "dex_liquidity_usd": Decimal("0"),
                "cex_depth_usd_1pct": Decimal("0"),
                "slippage_estimate_buy_10k_bps": Decimal("100"),
                "slippage_estimate_sell_10k_bps": Decimal("100"),
                "raw_payload": {"search": search},
            }
        pool = pools[0]
        attrs = pool.get("attributes", {})
        liquidity = Decimal(str(attrs.get("reserve_in_usd") or "0"))
        buy_impact = Decimal(str(attrs.get("price_impact_percentage", {}).get("buy", "0.5")))
        sell_impact = Decimal(str(attrs.get("price_impact_percentage", {}).get("sell", "0.5")))
        return {
            "asset_symbol": symbol.upper(),
            "venue": "geckoterminal",
            "venue_type": "dex",
            "chain": chain,
            "pool_id": pool.get("id"),
            "dex_liquidity_usd": liquidity,
            "cex_depth_usd_1pct": Decimal("0"),
            "slippage_estimate_buy_10k_bps": buy_impact * Decimal("100"),
            "slippage_estimate_sell_10k_bps": sell_impact * Decimal("100"),
            "raw_payload": {"search": search},
        }
