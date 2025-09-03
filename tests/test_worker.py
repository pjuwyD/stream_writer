import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from stream_writer.worker import process_batch, normalize_params

@pytest.mark.asyncio
@patch("stream_writer.worker.execute_query", new_callable=AsyncMock)
@patch("stream_writer.worker.execute_bulk", new_callable=AsyncMock)
async def test_process_batch_calls_execute(mock_bulk, mock_query):
    messages = [
        '{"query": "INSERT INTO t VALUES (%s)", "params": ["2025-09-02T12:00:00"], "bulk": false}',
        '{"query": "INSERT INTO t VALUES (%s)", "params": ["2025-09-02T13:00:00"], "bulk": true}'
    ]
    await process_batch(messages)
    assert mock_query.await_count == 1
    assert mock_bulk.await_count == 1

def test_normalize_params_datetime():
    params = ["2025-09-02T12:00:00", "abc"]
    result = normalize_params(params)
    from datetime import datetime
    assert isinstance(result[0], datetime)
    assert result[1] == "abc"

@pytest.mark.asyncio
@patch("stream_writer.worker.execute_query", new_callable=AsyncMock)
@patch("stream_writer.worker.execute_bulk", new_callable=AsyncMock)
@patch("stream_writer.worker.logger")
async def test_process_batch_handles_bad_json(mock_logger, mock_bulk, mock_query):
    messages = [
        '{"query": "INSERT INTO t VALUES (%s)", "params": ["2025-09-02T12:00:00"], "bulk": false}',
        '{"query": "INSERT INTO t VALUES (%s)", "params": ["2025-09-02T13:00:00"], "bulk": true}',
        '{"query": "BAD JSON'  # malformed JSON
    ]

    await process_batch(messages)

    # Regular messages are still processed
    assert mock_query.await_count == 1
    assert mock_bulk.await_count == 1

    # Logger should have recorded an error for the bad JSON
    mock_logger.error.assert_called()
    args, _ = mock_logger.error.call_args
    assert "Failed to parse message" in args[0]