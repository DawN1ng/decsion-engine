import asyncio

from app.core.logging import configure_logging
from app.jobs.scheduler import build_scheduler


async def main() -> None:
    configure_logging()
    scheduler = build_scheduler()
    scheduler.start()
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
