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
        oi_history = await self.http.get(
            f"{self.base_url}/v5/market/open-interest",
            params={"category": "linear", "symbol": pair, "intervalTime": "5min", "limit": 24},
        )
        funding = await self.http.get(
            f"{self.base_url}/v5/market/funding/history",
            params={"category": "linear", "symbol": pair, "limit": 42},
        )

        item = tickers["result"]["list"][0]
        rates = [Decimal(x["fundingRate"]) for x in funding.get("result", {}).get("list", []) if x.get("fundingRate") is not None]
        current_rate = rates[0] if rates else Decimal(item.get("fundingRate", "0"))
        mean = sum(rates) / Decimal(len(rates)) if rates else Decimal("0")
        std = Decimal(str(pstdev([float(r) for r in rates]))) if len(rates) > 1 else Decimal("0")
        zscore = (current_rate - mean) / std if std else Decimal("0")

        current_oi, change_1h = self._compute_oi_metrics(oi_history.get("result", {}).get("list", []))

        return {
            "asset_symbol": symbol.upper(),
            "venue": "bybit",
            "contract_type": "perpetual",
            "open_interest_usd": current_oi,
            "open_interest_change_1h_pct": change_1h,
            "funding_rate": current_rate,
            "funding_rate_zscore_7d": zscore,
            "raw_payload": {"tickers": tickers, "funding": funding, "open_interest_history": oi_history},
        }

    def _compute_oi_metrics(self, rows: list[dict[str, Any]]) -> tuple[Decimal, Decimal | None]:
        if not rows:
            return Decimal("0"), None
        parsed = []
        for row in rows:
            if row.get("openInterest") and row.get("timestamp"):
                parsed.append((int(row["timestamp"]), Decimal(row["openInterest"])))
        if not parsed:
            return Decimal("0"), None
        parsed.sort(key=lambda x: x[0])
        latest_ts, latest_oi = parsed[-1]
        target_ts = latest_ts - 3600 * 1000
        baseline_candidates = [x for x in parsed if x[0] <= target_ts]
        if not baseline_candidates:
            return latest_oi, None
        baseline_oi = baseline_candidates[-1][1]
        if baseline_oi == 0:
            return latest_oi, None
        change = ((latest_oi - baseline_oi) / baseline_oi) * Decimal("100")
        return latest_oi, change
