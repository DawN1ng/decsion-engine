from apscheduler.schedulers.asyncio import AsyncIOScheduler


def build_scheduler() -> AsyncIOScheduler:
    return AsyncIOScheduler(timezone="UTC")
