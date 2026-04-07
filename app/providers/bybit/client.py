from app.providers.base import ProviderClient


class BybitMarketClient(ProviderClient):
    async def fetch(self, symbol: str) -> dict:
        return {"symbol": symbol, "open_interest_change_pct": "0", "funding_rate": "0", "source": "bybit"}
