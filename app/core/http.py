from __future__ import annotations

import asyncio
from collections import deque
from datetime import datetime, timezone
from typing import Any

import httpx
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

from app.core.config import get_settings


class RateLimiter:
    def __init__(self, calls_per_second: float) -> None:
        self.calls_per_second = calls_per_second
        self._calls: deque[datetime] = deque()

    async def wait(self) -> None:
        now = datetime.now(timezone.utc)
        while self._calls and (now - self._calls[0]).total_seconds() > 1:
            self._calls.popleft()
        if len(self._calls) >= int(self.calls_per_second):
            sleep_for = 1 - (now - self._calls[0]).total_seconds()
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
        self._calls.append(datetime.now(timezone.utc))


class BaseHttpClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.timeout = settings.provider_timeout_seconds
        self.retries = settings.provider_retries
        self.limiter = RateLimiter(settings.provider_rate_limit_per_second)
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def get(self, url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
        async for attempt in AsyncRetrying(
            wait=wait_exponential(multiplier=1, min=1, max=8),
            stop=stop_after_attempt(self.retries),
            reraise=True,
        ):
            with attempt:
                await self.limiter.wait()
                resp = await self._client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                return resp.json()
        raise RuntimeError("unreachable")

    async def close(self) -> None:
        await self._client.aclose()
