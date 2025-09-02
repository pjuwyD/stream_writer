import aiomysql
from .config import Config

# Create a connection pool
async def create_pool():
    return await aiomysql.create_pool(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        db=Config.MYSQL_DB,
        minsize=5,
        maxsize=10,
        autocommit=True
    )

# Global pool variable
pool = None

async def init_db():
    global pool
    pool = await create_pool()

async def execute_query(query: str, params: list):
    """Execute a single query with parameters."""
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query, params)

async def execute_bulk(query: str, params_list: list):
    """Execute a query multiple times with different parameter sets."""
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.executemany(query, params_list)