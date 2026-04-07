from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.providers.base import ProviderClient


class OnchainClusterFlowProvider(ProviderClient):
    async def fetch(self, symbol: str, **kwargs: Any) -> dict[str, Any]:
        settings = get_settings()
        wallets = settings.load_yaml("wallet_labels.yaml")
        rows = self._load_rows(settings.onchain_manual_flows_path)
        symbol_rows = [r for r in rows if r.get("asset_symbol", "").upper() == symbol.upper()]

        exchange = set(wallets.get("exchange_clusters", []))
        team = set(wallets.get("team_wallets", []))
        foundation = set(wallets.get("foundation_wallets", []))
        whales = set(wallets.get("whale_watchlist", []))

        whale_inflow, whale_outflow = Decimal("0"), Decimal("0")
        team_to_exchange, foundation_to_exchange = Decimal("0"), Decimal("0")
        labeled = 0

        for row in symbol_rows:
            frm, to = row.get("from"), row.get("to")
            amount = Decimal(str(row.get("usd_amount", 0)))
            if frm in whales:
                whale_outflow += amount
                labeled += 1
            if to in whales:
                whale_inflow += amount
                labeled += 1
            if frm in team and to in exchange:
                team_to_exchange += amount
                labeled += 1
            if frm in foundation and to in exchange:
                foundation_to_exchange += amount
                labeled += 1

        return {
            "asset_symbol": symbol.upper(),
            "chain": kwargs.get("chain", "ethereum"),
            "whale_inflow_usd": whale_inflow,
            "whale_outflow_usd": whale_outflow,
            "whale_netflow_usd": whale_inflow - whale_outflow,
            "team_to_exchange_usd": team_to_exchange,
            "foundation_to_exchange_usd": foundation_to_exchange,
            "labeled_flow_count": labeled,
            "raw_payload": {"matched_rows": symbol_rows},
        }

    def _load_rows(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
