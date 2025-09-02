import asyncio
import uvloop
from .config import Config
from .worker import worker
from .db import init_db


async def main():
    # Initialize database connection pool
    await init_db()
    # Create one worker task per Redis queue defined in the config
    tasks = [asyncio.create_task(worker(q)) for q in Config.REDIS_QUEUES]
    # Run all workers concurrently forever
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # Replace asyncio's default event loop with uvloop for better performance
    uvloop.install()
    asyncio.run(main())