import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from stream_writer.db import execute_query, execute_bulk

@pytest.mark.asyncio
@patch("stream_writer.db.pool")
async def test_execute_query(mock_pool):
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()

    # Setup async context manager for acquire
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = None

    # Setup async context manager for cursor
    mock_conn.cursor = MagicMock()
    mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__aexit__.return_value = None

    await execute_query("SELECT 1", [1])
    mock_cursor.execute.assert_awaited_with("SELECT 1", [1])


@pytest.mark.asyncio
@patch("stream_writer.db.pool")
async def test_execute_bulk(mock_pool):
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()

    # Setup async context manager for acquire
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = None

    # Setup async context manager for cursor
    mock_conn.cursor = MagicMock()
    mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__aexit__.return_value = None

    await execute_bulk("INSERT INTO t VALUES (%s)", [[1], [2]])
    mock_cursor.executemany.assert_awaited_with("INSERT INTO t VALUES (%s)", [[1], [2]])