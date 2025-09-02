import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from stream_writer.worker import process_batch, normalize_params

@pytest.mark.asyncio
@patch("stream_writer.worker.execute_query", new_callable=AsyncMock)
@patch("stream_writer.worker.execute_bulk", new_callable=AsyncMock)
def test_process_batch_calls_execute(mock_bulk, mock_query):
    messages = [
        '{"query": "INSERT INTO t VALUES (%s)", "params": ["2025-09-02T12:00:00"], "bulk": false}',
        '{"query": "INSERT INTO t VALUES (%s)", "params": ["2025-09-02T13:00:00"], "bulk": true}'
    ]
    asyncio.run(process_batch(messages))
    assert mock_query.await_count == 1
    assert mock_bulk.await_count == 1

def test_normalize_params_datetime():
    params = ["2025-09-02T12:00:00", "abc"]
    result = normalize_params(params)
    from datetime import datetime
    assert isinstance(result[0], datetime)
    assert result[1] == "abc"