from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.providers.base import ProviderClient


class BinanceMarketClient(ProviderClient):
    base_url = "https://api.binance.com"

    async def fetch(self, symbol: str, quote_currency: str = "USDT", **kwargs: Any) -> dict[str, Any]:
        pair = f"{symbol.upper()}{quote_currency.upper()}"
        ticker_24h = await self.http.get(f"{self.base_url}/api/v3/ticker/24hr", params={"symbol": pair})
        book_ticker = await self.http.get(f"{self.base_url}/api/v3/ticker/bookTicker", params={"symbol": pair})
        order_book = await self.http.get(f"{self.base_url}/api/v3/depth", params={"symbol": pair, "limit": 100})

        bid = Decimal(book_ticker["bidPrice"])
        ask = Decimal(book_ticker["askPrice"])
        mid = (bid + ask) / Decimal("2") if bid and ask else Decimal(ticker_24h["lastPrice"])
        spread_bps = ((ask - bid) / mid) * Decimal("10000") if mid else Decimal("0")

        depth = Decimal("0")
        for price, qty in order_book.get("bids", [])[:20]:
            p, q = Decimal(price), Decimal(qty)
            if p >= mid * Decimal("0.99"):
                depth += p * q
        for price, qty in order_book.get("asks", [])[:20]:
            p, q = Decimal(price), Decimal(qty)
            if p <= mid * Decimal("1.01"):
                depth += p * q

        return {
            "asset_symbol": symbol.upper(),
            "venue": "binance",
            "last_price": Decimal(ticker_24h["lastPrice"]),
            "volume_24h": Decimal(ticker_24h["quoteVolume"]),
            "bid_ask_spread_bps": spread_bps,
            "orderbook_depth_usd_1pct": depth,
            "raw_payload": {"ticker_24h": ticker_24h, "book_ticker": book_ticker, "order_book": order_book},
        }


class BinanceWalletClient(ProviderClient):
    async def fetch(self, symbol: str, **kwargs: Any) -> dict[str, Any]:
        settings = get_settings()
        mode = settings.cex_flow_mode
        if mode == "manual_cluster":
            return self._manual_cluster(symbol, settings.cex_manual_flows_path)
        if mode == "real_cluster":
            return {
                "asset_symbol": symbol.upper(),
                "venue": "binance",
                "inflow_usd": Decimal("0"),
                "outflow_usd": Decimal("0"),
                "netflow_usd": Decimal("0"),
                "source_type": "real_cluster",
                "trust_level": "high",
                "raw_payload": {"status": "hook_not_implemented"},
            }
        return self._derived(symbol, kwargs.get("market") or {})

    def _derived(self, symbol: str, market: dict[str, Any]) -> dict[str, Any]:
        volume = Decimal(str(market.get("volume_24h", "0")))
        flow = volume * Decimal("0.015")
        return {
            "asset_symbol": symbol.upper(),
            "venue": "binance",
            "inflow_usd": flow,
            "outflow_usd": flow * Decimal("1.03"),
            "netflow_usd": (flow * Decimal("1.03")) - flow,
            "source_type": "derived",
            "trust_level": "low",
            "raw_payload": {"derived_from": "binance_24h_quote_volume", "volume_24h": str(volume)},
        }

    def _manual_cluster(self, symbol: str, path: Path) -> dict[str, Any]:
        rows = []
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                rows = json.load(f)
        rows = [r for r in rows if r.get("asset_symbol", "").upper() == symbol.upper() and r.get("venue", "binance") == "binance"]
        inflow = sum(Decimal(str(r.get("inflow_usd", 0))) for r in rows)
        outflow = sum(Decimal(str(r.get("outflow_usd", 0))) for r in rows)
        return {
            "asset_symbol": symbol.upper(),
            "venue": "binance",
            "inflow_usd": inflow,
            "outflow_usd": outflow,
            "netflow_usd": outflow - inflow,
            "source_type": "manual_cluster",
            "trust_level": "medium",
            "raw_payload": {"rows": rows, "mode": "manual_cluster"},
        }
