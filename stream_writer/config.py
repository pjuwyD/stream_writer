import os


class Config:
    # MySQL config
    MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_DB = os.getenv("MYSQL_DB", "live")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")

    # Redis standalone config
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))

    # Redis Sentinel config
    REDIS_USE_SENTINEL = os.getenv("REDIS_USE_SENTINEL", "false").lower() == "true"
    REDIS_SENTINELS = os.getenv("REDIS_SENTINELS", "")  # "host1:26379,host2:26379"
    REDIS_MASTER_NAME = os.getenv("REDIS_MASTER_NAME", "mymaster")

    # Queues
    REDIS_QUEUES = os.getenv("REDIS_QUEUES", "").split(",")  # mandatory list

    # Batching
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 50))
    BLOCK_TIMEOUT = int(os.getenv("BLOCK_TIMEOUT", 5))  # sec for BLPOP blocking
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()