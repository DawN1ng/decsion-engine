from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from app.providers.base import ProviderClient


class DefiLlamaClient(ProviderClient):
    base_url = "https://api.llama.fi"

    def __init__(self) -> None:
        super().__init__()
        self._cache: dict[str, tuple[datetime, dict[str, Any]]] = {}

    async def fetch(self, symbol: str, **kwargs: Any) -> dict[str, Any]:
        key = symbol.upper()
        now = datetime.now(timezone.utc)
        if key in self._cache and self._cache[key][0] > now - timedelta(minutes=30):
            return self._cache[key][1]
        chains = await self.http.get(f"{self.base_url}/v2/chains")
        match = next((x for x in chains if x.get("tokenSymbol", "").upper() == key), None)
        payload = {
            "asset_symbol": key,
            "macro_tvl_usd": Decimal(str(match.get("tvl", 0))) if match else Decimal("0"),
            "raw_payload": {"chains": chains[:20]},
        }
        self._cache[key] = (now, payload)
        return payload
