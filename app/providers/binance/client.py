from __future__ import annotations

from decimal import Decimal
from typing import Any

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
        # Public endpoint limitation: use derived flow placeholder from market volume/volatility until exchange-flow feed is wired.
        market = kwargs.get("market") or {}
        volume = Decimal(str(market.get("volume_24h", "0")))
        flow = volume * Decimal("0.015")
        return {
            "asset_symbol": symbol.upper(),
            "venue": "binance",
            "inflow_usd": flow,
            "outflow_usd": flow * Decimal("1.03"),
            "netflow_usd": (flow * Decimal("1.03")) - flow,
            "source_type": "derived",
            "raw_payload": {"derived_from": "binance_24h_quote_volume", "volume_24h": str(volume)},
        }
