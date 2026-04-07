from app.providers.base import ProviderClient


class DefiLlamaClient(ProviderClient):
    async def fetch(self, symbol: str) -> dict:
        return {"symbol": symbol, "spread_bps": "10", "slippage_bps": "12", "depth_usd": "100000", "source": "defillama"}
