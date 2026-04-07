from app.providers.base import ProviderClient


class CoinGeckoOnchainClient(ProviderClient):
    async def fetch(self, symbol: str) -> dict:
        return {"symbol": symbol, "whale_accumulation": "0", "team_to_exchange": "0", "source": "coingecko"}
