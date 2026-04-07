import pytest
from decimal import Decimal

from app.providers.binance.client import BinanceMarketClient


@pytest.mark.asyncio
async def test_binance_parser_from_public_shapes(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_get(url: str, params=None, headers=None):
        if "ticker/24hr" in url:
            return {"lastPrice": "100", "quoteVolume": "2000000"}
        if "bookTicker" in url:
            return {"bidPrice": "99.9", "askPrice": "100.1"}
        return {"bids": [["99.5", "10"]], "asks": [["100.5", "10"]]}

    client = BinanceMarketClient()
    monkeypatch.setattr(client.http, "get", fake_get)
    payload = await client.fetch("ETH")
    assert payload["asset_symbol"] == "ETH"
    assert payload["last_price"] == Decimal("100")
    assert payload["volume_24h"] == Decimal("2000000")
