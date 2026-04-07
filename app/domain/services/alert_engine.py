from __future__ import annotations

from datetime import datetime, timezone

from app.domain.models.entities import Alert, CexFlowSnapshot, OnchainFlow, Signal


class AlertEngine:
    def build_data_alerts(
        self,
        symbol: str,
        cex_flow: CexFlowSnapshot | None,
        onchain: OnchainFlow | None,
        signal: Signal | None,
    ) -> list[Alert]:
        alerts: list[Alert] = []
        now = datetime.now(timezone.utc)
        if cex_flow and cex_flow.netflow_usd < 0 and cex_flow.trust_level != "low":
            alerts.append(
                Alert(
                    asset_symbol=symbol,
                    ts=now,
                    severity="medium",
                    alert_type="HIGH_EXCHANGE_INFLOW",
                    message=f"{symbol} net inflow into exchange increased",
                    details_json={"netflow_usd": str(cex_flow.netflow_usd), "venue": cex_flow.venue, "trust_level": cex_flow.trust_level},
                )
            )
        if onchain and (onchain.team_to_exchange_usd + onchain.foundation_to_exchange_usd) > 0:
            alerts.append(
                Alert(
                    asset_symbol=symbol,
                    ts=now,
                    severity="high",
                    alert_type="TEAM_TO_EXCHANGE",
                    message=f"{symbol} team/foundation sent tokens toward exchange clusters",
                    details_json={
                        "team_to_exchange_usd": str(onchain.team_to_exchange_usd),
                        "foundation_to_exchange_usd": str(onchain.foundation_to_exchange_usd),
                    },
                )
            )
        if signal and signal.action in {"BUILD_LONG", "REDUCE_OR_SHORT", "EXIT"}:
            kind = "SIGNAL_UPGRADE" if signal.action == "BUILD_LONG" else "SIGNAL_DOWNGRADE"
            alerts.append(
                Alert(
                    asset_symbol=symbol,
                    ts=now,
                    severity="high" if kind == "SIGNAL_DOWNGRADE" else "info",
                    alert_type=kind,
                    message=f"{symbol} signal action={signal.action}",
                    details_json={"action": signal.action, "confidence": str(signal.confidence)},
                )
            )
        return alerts
