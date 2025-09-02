import asyncio
import json
from datetime import datetime
from .config import Config
from .db import execute_query, execute_bulk
from .redis_client import get_redis_connection
import logging

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def normalize_params(params):
    """
    Ensure all params are proper types for DB driver:
    - Convert ISO datetime strings to datetime objects
    - Ensure numeric types are numeric
    """
    normalized = []
    for p in params:
        if isinstance(p, str):
            # Try converting ISO datetime strings
            try:
                normalized.append(datetime.fromisoformat(p))
            except ValueError:
                normalized.append(p)
        else:
            normalized.append(p)
    return tuple(normalized)


async def process_batch(messages):
    """
    Process a batch of messages from Redis.
    Bulk messages are executed together.
    """
    bulk_messages = []
    non_bulk_messages = []

    for msg_str in messages:
        try:
            msg = json.loads(msg_str)
            query = msg["query"]
            params = normalize_params(msg.get("params", []))
            bulk = msg.get("bulk", False)
            logger.debug(f"Parsed message: {msg}")
            if bulk:
                bulk_messages.append(params)
            else:
                non_bulk_messages.append((query, params))

        except Exception as e:
            logger.error(f"Failed to parse message {msg_str}: {e}")

    # Execute non-bulk queries immediately
    for query, params in non_bulk_messages:
        logger.info(f"Executing non-bulk query: {query} with params: {params}")
        await execute_query(query, params)

    # Execute bulk queries together
    if bulk_messages:
        first_query = json.loads(messages[0])["query"]
        logger.info(f"Executing bulk query: {first_query} with {len(bulk_messages)} sets of params")
        await execute_bulk(first_query, bulk_messages)


async def worker(queue: str):
    """
    Continuously pops messages from Redis queue and processes in batches.
    """
    redis = await get_redis_connection()
    logger.info(f"Worker started for queue: {queue}")

    while True:
        try:
            # Wait for first message
            item = await redis.blpop(queue, timeout=Config.BLOCK_TIMEOUT)
            if not item:
                logger.debug("No item received from queue (timeout).")
                await asyncio.sleep(0.1)
                continue

            _, first_msg = item
            messages = [first_msg]
            logger.debug(f"Received first message: {first_msg}")

            #Drain up to BATCH_SIZE - 1 more with a short timeout
            for _ in range(int(Config.BATCH_SIZE) - 1):
                try:
                    # Wait up to 0.1 seconds for next message
                    next_item = await redis.blpop(queue, timeout=0.1)
                    if not next_item:
                        break
                    _, next_msg = next_item
                    messages.append(next_msg)
                    logger.debug(f"Drained message: {next_msg}")
                except:
                    break

            logger.info(f"Processing batch of {len(messages)} messages.")
            await process_batch(messages)

        except Exception as e:
            logger.error(f"Worker error on queue {queue}: {e}", exc_info=True)
            await asyncio.sleep(1)
