from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.core.http import BaseHttpClient


class ProviderClient(ABC):
    def __init__(self) -> None:
        self.http = BaseHttpClient()

    @abstractmethod
    async def fetch(self, symbol: str, **kwargs: Any) -> dict[str, Any]:
        ...
