from __future__ import annotations

from decimal import Decimal
from statistics import pstdev
from typing import Any

from app.providers.base import ProviderClient


class BybitMarketClient(ProviderClient):
    base_url = "https://api.bybit.com"

    async def fetch(self, symbol: str, quote_currency: str = "USDT", **kwargs: Any) -> dict[str, Any]:
        pair = f"{symbol.upper()}{quote_currency.upper()}"
        tickers = await self.http.get(
            f"{self.base_url}/v5/market/tickers",
            params={"category": "linear", "symbol": pair},
        )
        funding = await self.http.get(
            f"{self.base_url}/v5/market/funding/history",
            params={"category": "linear", "symbol": pair, "limit": 20},
        )
        item = tickers["result"]["list"][0]
        history = funding.get("result", {}).get("list", [])
        rates = [Decimal(x["fundingRate"]) for x in history if x.get("fundingRate") is not None]
        current_rate = Decimal(item.get("fundingRate", "0")) if item.get("fundingRate") else (rates[0] if rates else Decimal("0"))
        mean = sum(rates) / Decimal(len(rates)) if rates else Decimal("0")
        std = Decimal(str(pstdev([float(r) for r in rates]))) if len(rates) > 1 else Decimal("0")
        zscore = (current_rate - mean) / std if std else Decimal("0")

        oi = Decimal(item.get("openInterestValue", "0"))
        oi_change = Decimal(item.get("openInterest", "0"))
        oi_change_1h_pct = Decimal("0")
        if oi:
            oi_change_1h_pct = (oi_change / oi) * Decimal("100")

        return {
            "asset_symbol": symbol.upper(),
            "venue": "bybit",
            "contract_type": "perpetual",
            "open_interest_usd": oi,
            "open_interest_change_1h_pct": oi_change_1h_pct,
            "funding_rate": current_rate,
            "funding_rate_zscore_7d": zscore,
            "raw_payload": {"tickers": tickers, "funding": funding},
        }
