from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.providers.base import ProviderClient


class CoinGeckoOnchainClient(ProviderClient):
    base_url = "https://api.geckoterminal.com/api/v2"

    async def fetch(self, symbol: str, chain: str = "eth", token_address: str | None = None, **kwargs: Any) -> dict[str, Any]:
        if token_address:
            pools_resp = await self.http.get(f"{self.base_url}/networks/{chain}/tokens/{token_address}/pools")
            pools = pools_resp.get("data", [])
            selected = self._select_best_pool(pools, symbol)
            method = "token_address_top_pool"
            raw = {"selection_method": method, "token_address": token_address, "pools_count": len(pools), "selected": selected}
            return self._to_snapshot(symbol, chain, selected, raw)

        search = await self.http.get(f"{self.base_url}/search/pools", params={"query": symbol.upper()})
        pools = search.get("data", [])
        selected = self._select_best_pool(pools, symbol)
        method = "symbol_search_ranked" if selected else "fallback_none"
        raw = {"selection_method": method, "pools_count": len(pools), "selected": selected}
        return self._to_snapshot(symbol, chain, selected, raw)

    def _select_best_pool(self, pools: list[dict[str, Any]], symbol: str) -> dict[str, Any] | None:
        ranked: list[tuple[Decimal, dict[str, Any]]] = []
        upper = symbol.upper()
        for pool in pools:
            attrs = pool.get("attributes", {})
            liq = Decimal(str(attrs.get("reserve_in_usd") or "0"))
            vol = Decimal(str((attrs.get("volume_usd") or {}).get("h24") or "0"))
            name = str(attrs.get("name", "")).upper()
            symbol_bonus = Decimal("1000000") if upper in name else Decimal("0")
            score = liq + (vol * Decimal("0.2")) + symbol_bonus
            ranked.append((score, pool))
        if not ranked:
            return None
        ranked.sort(key=lambda x: x[0], reverse=True)
        return ranked[0][1]

    def _to_snapshot(self, symbol: str, chain: str, selected: dict[str, Any] | None, raw: dict[str, Any]) -> dict[str, Any]:
        if not selected:
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
                "raw_payload": raw,
            }
        attrs = selected.get("attributes", {})
        liquidity = Decimal(str(attrs.get("reserve_in_usd") or "0"))
        buy_impact = Decimal(str(attrs.get("price_impact_percentage", {}).get("buy", "0.5")))
        sell_impact = Decimal(str(attrs.get("price_impact_percentage", {}).get("sell", "0.5")))
        return {
            "asset_symbol": symbol.upper(),
            "venue": "geckoterminal",
            "venue_type": "dex",
            "chain": chain,
            "pool_id": selected.get("id"),
            "dex_liquidity_usd": liquidity,
            "cex_depth_usd_1pct": Decimal("0"),
            "slippage_estimate_buy_10k_bps": buy_impact * Decimal("100"),
            "slippage_estimate_sell_10k_bps": sell_impact * Decimal("100"),
            "raw_payload": raw,
        }
