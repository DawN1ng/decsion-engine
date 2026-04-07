from __future__ import annotations

from decimal import Decimal


class NormalizationService:
    @staticmethod
    def clamp(value: Decimal, low: Decimal = Decimal("-1"), high: Decimal = Decimal("1")) -> Decimal:
        return max(low, min(high, value))

    @staticmethod
    def scale_ratio(value: Decimal, divisor: Decimal) -> Decimal:
        if divisor == 0:
            return Decimal("0")
        return value / divisor
