from abc import ABC, abstractmethod

from app.core.http import BaseHttpClient


class ProviderClient(ABC):
    def __init__(self) -> None:
        self.http = BaseHttpClient()

    @abstractmethod
    async def fetch(self, symbol: str) -> dict:
        ...
