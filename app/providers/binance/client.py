from app.providers.base import ProviderClient


class BinanceMarketClient(ProviderClient):
    async def fetch(self, symbol: str) -> dict:
        return {"symbol": symbol, "price": "0", "cex_inflow": "0", "cex_outflow": "0", "source": "binance"}


class BinanceWalletClient(ProviderClient):
    async def fetch(self, symbol: str) -> dict:
        return {"symbol": symbol, "wallet_flows": [], "source": "binance_wallet"}
