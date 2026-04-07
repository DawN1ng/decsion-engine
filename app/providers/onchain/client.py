from app.providers.base import ProviderClient


class OnchainClusterFlowProvider(ProviderClient):
    async def fetch(self, symbol: str) -> dict:
        return {"symbol": symbol, "cluster_exchange_inflow": "0", "cluster_exchange_outflow": "0", "source": "onchain"}
