FROM python:3.11-slim

WORKDIR /stream_writer

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY stream_writer ./stream_writer

CMD ["python", "-m", "stream_writer.main"]