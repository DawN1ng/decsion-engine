import asyncio
from decimal import Decimal

from app.providers.binance.client import BinanceMarketClient, BinanceWalletClient
from app.providers.bybit.client import BybitMarketClient
from app.providers.coingecko.client import CoinGeckoOnchainClient


def test_binance_parser_from_public_shapes(monkeypatch) -> None:
    async def fake_get(url: str, params=None, headers=None):
        if "ticker/24hr" in url:
            return {"lastPrice": "100", "quoteVolume": "2000000"}
        if "bookTicker" in url:
            return {"bidPrice": "99.9", "askPrice": "100.1"}
        return {"bids": [["99.5", "10"]], "asks": [["100.5", "10"]]}

    client = BinanceMarketClient()
    monkeypatch.setattr(client.http, "get", fake_get)
    payload = asyncio.run(client.fetch("ETH"))
    assert payload["asset_symbol"] == "ETH"
    assert payload["last_price"] == Decimal("100")


def test_bybit_open_interest_change_from_series(monkeypatch) -> None:
    async def fake_get(url: str, params=None, headers=None):
        if "tickers" in url:
            return {"result": {"list": [{"fundingRate": "0.01"}]}}
        if "open-interest" in url:
            return {
                "result": {
                    "list": [
                        {"timestamp": "0", "openInterest": "100"},
                        {"timestamp": str(3600 * 1000), "openInterest": "120"},
                    ]
                }
            }
        return {"result": {"list": [{"fundingRate": "0.01"}, {"fundingRate": "0.02"}]}}

    client = BybitMarketClient()
    monkeypatch.setattr(client.http, "get", fake_get)
    payload = asyncio.run(client.fetch("ETH"))
    assert payload["open_interest_usd"] == Decimal("120")
    assert payload["open_interest_change_1h_pct"] == Decimal("20")


def test_gecko_prefers_token_address_path(monkeypatch) -> None:
    async def fake_get(url: str, params=None, headers=None):
        return {
            "data": [
                {"id": "pool_low", "attributes": {"reserve_in_usd": "1000", "name": "ETH/USDC"}},
                {"id": "pool_high", "attributes": {"reserve_in_usd": "9000", "name": "ETH/USDT"}},
            ]
        }

    client = CoinGeckoOnchainClient()
    monkeypatch.setattr(client.http, "get", fake_get)
    payload = asyncio.run(client.fetch("ETH", chain="eth", token_address="0xabc"))
    assert payload["pool_id"] == "pool_high"
    assert payload["raw_payload"]["selection_method"] == "token_address_top_pool"


def test_cex_manual_cluster_mode(monkeypatch, tmp_path) -> None:
    path = tmp_path / "flows.json"
    path.write_text('[{"asset_symbol":"ETH","venue":"binance","inflow_usd":100,"outflow_usd":180}]')

    from app.core.config import Settings

    monkeypatch.setattr("app.providers.binance.client.get_settings", lambda: Settings(cex_flow_mode="manual_cluster", cex_manual_flows_path=path))
    payload = BinanceWalletClient()._manual_cluster("ETH", path)
    assert payload["source_type"] == "manual_cluster"
    assert payload["trust_level"] == "medium"


def test_gecko_symbol_fallback_ranked(monkeypatch) -> None:
    async def fake_get(url: str, params=None, headers=None):
        return {
            "data": [
                {"id": "pool_a", "attributes": {"reserve_in_usd": "1000", "name": "AAA/USDC", "volume_usd": {"h24": "500"}}},
                {"id": "pool_b", "attributes": {"reserve_in_usd": "3000", "name": "ETH/USDT", "volume_usd": {"h24": "400"}}},
            ]
        }

    client = CoinGeckoOnchainClient()
    monkeypatch.setattr(client.http, "get", fake_get)
    payload = asyncio.run(client.fetch("ETH", chain="eth", token_address=None))
    assert payload["pool_id"] == "pool_b"
    assert payload["raw_payload"]["selection_method"] == "symbol_search_ranked"


def test_gecko_empty_result_path(monkeypatch) -> None:
    async def fake_get(url: str, params=None, headers=None):
        return {"data": []}

    client = CoinGeckoOnchainClient()
    monkeypatch.setattr(client.http, "get", fake_get)
    payload = asyncio.run(client.fetch("ETH", chain="eth", token_address=None))
    assert payload["pool_id"] is None
    assert payload["raw_payload"]["selection_method"] == "fallback_none"


def test_bybit_oi_change_unavailable_when_not_enough_history(monkeypatch) -> None:
    async def fake_get(url: str, params=None, headers=None):
        if "tickers" in url:
            return {"result": {"list": [{"fundingRate": "0.01"}]}}
        if "open-interest" in url:
            return {"result": {"list": [{"timestamp": "3600000", "openInterest": "120"}]}}
        return {"result": {"list": [{"fundingRate": "0.01"}]}}

    client = BybitMarketClient()
    monkeypatch.setattr(client.http, "get", fake_get)
    payload = asyncio.run(client.fetch("ETH"))
    assert payload["open_interest_change_1h_pct"] is None
