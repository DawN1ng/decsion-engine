from datetime import datetime, timezone

from app.domain.models.entities import Alert, Signal


class AlertEngine:
    def build_alert(self, signal: Signal) -> Alert | None:
        if signal.action in {"BUILD_LONG", "REDUCE_OR_SHORT"}:
            return Alert(
                asset_symbol=signal.asset_symbol,
                ts=datetime.now(timezone.utc),
                severity="high" if signal.action == "REDUCE_OR_SHORT" else "info",
                message=f"{signal.asset_symbol} action changed to {signal.action}",
            )
        return None
