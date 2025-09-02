import redis.asyncio as redis
from redis.sentinel import Sentinel
from .config import Config


async def get_redis_connection() -> redis.Redis:
    """
    Return a Redis connection, either standalone or via Sentinel.
    """
    if Config.REDIS_USE_SENTINEL:
        # Parse sentinel hosts: "host1:26379,host2:26379"
        sentinels = [
            tuple(s.strip().split(":")) for s in Config.REDIS_SENTINELS.split(",") if s.strip()
        ]
        sentinels = [(host, int(port)) for host, port in sentinels]
        sentinel = Sentinel(sentinels, socket_timeout=2, decode_responses=True)
        return sentinel.master_for(
            service_name=Config.REDIS_MASTER_NAME,
            db=Config.REDIS_DB,
            decode_responses=True,
        )
    else:
        return redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB,
            decode_responses=True,
        )