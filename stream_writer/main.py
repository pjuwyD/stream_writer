import asyncio
import uvloop
from .config import Config
from .worker import worker
from .db import init_db


async def main():
    await init_db()
    tasks = [asyncio.create_task(worker(q)) for q in Config.REDIS_QUEUES]
    
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    uvloop.install()

    asyncio.run(main())