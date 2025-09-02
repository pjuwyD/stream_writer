# stream_writer

Microservice that reads from Redis and writes asynchronously to MySQL DB.

## Features

- Reads messages from Redis queues (standalone or Sentinel)
- Batches and writes data to MySQL asynchronously
- Configurable batch size and logging level
- Supports bulk and single queries
- Scaling: this service can be scaled horizontally by running multiple containers that listen to the same Redis queue. This is safe because Redis queue operations like BLPOP and LPOP are atomic: when a worker pops a message from the queue, that message is removed and cannot be processed by another worker.


## Project Structure

```
stream_writer/
├── stream_writer/
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── worker.py
│   ├── redis_client.py
├── tests/
│   ├── test_db.py
│   ├── test_worker.py
├── requirements.txt
├── Dockerfile
├── README.md
```

## Setup

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

2. **Environment variables:**  
   Set these as needed (defaults shown):
   - `MYSQL_HOST` (default: `mysql`)
   - `MYSQL_PORT` (default: `3306`)
   - `MYSQL_DB` (default: `live`)
   - `MYSQL_USER` (default: `root`)
   - `MYSQL_PASSWORD` (default: `root`)
   - `REDIS_HOST` (default: `redis`)
   - `REDIS_PORT` (default: `6379`)
   - `REDIS_DB` (default: `0`)
   - `REDIS_USE_SENTINEL` (default: `false`)
   - `REDIS_SENTINELS` (default: `""`)
   - `REDIS_MASTER_NAME` (default: `mymaster`)
   - `REDIS_QUEUES` (comma-separated list, e.g. `queue1,queue2`)
   - `BATCH_SIZE` (default: `50`)
   - `BLOCK_TIMEOUT` (default: `5`)
   - `LOG_LEVEL` (default: `INFO`)

## Usage

### Run locally

First, create and activate a Python virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then start the service:

```sh
python -m stre
```

## Logging

Set the `LOG_LEVEL` environment variable to control verbosity (`DEBUG`, `INFO`, `ERROR`, etc.).

## Testing

Tests are located in the `tests/` directory and use `pytest` and `pytest-asyncio`.

Install test dependencies:

```sh
pip install pytest pytest-asyncio
```

Run tests (from project root):

```sh
PYTHONPATH=./ pytest
```

## Docker: Build Image and Run with Compose

### Build the Docker Image

From the project root (`/opt/stream_writer`), run:

```sh
docker build -t stream-ms:latest -f docker/Dockerfile .
```

### Run with Docker Compose

Make sure your `docker-compose.yml` is in the `docker/` directory.  
Start the service with:

```sh
docker compose -f docker/docker-compose.yml up
```

This will launch the container with the environment variables specified in the compose file.  
You can scale horizontally by increasing the number of replicas in the compose file or running more containers.

## Kubernetes: Run as a Job

To run this service as a Kubernetes Job, create a manifest like the following and apply it to your cluster:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: stream-writer-job
spec:
  template:
    spec:
      containers:
        - name: stream-writer
          image: stream-ms:latest
          env:
            - name: MYSQL_HOST
              value: "mysql"
            - name: MYSQL_PORT
              value: "3306"
            - name: MYSQL_DB
              value: "live"
            - name: MYSQL_USER
              value: "root"
            - name: MYSQL_PASSWORD
              value: "root"
            - name: REDIS_HOST
              value: "redis"
            - name: REDIS_PORT
              value: "6379"
            - name: REDIS_DB
              value: "0"
            - name: REDIS_QUEUES
              value: "finishedSC,finishedCamp"
            - name: BATCH_SIZE
              value: "50"
            - name: BLOCK_TIMEOUT
              value: "5"
            # Add Sentinel variables if needed
            # - name: REDIS_USE_SENTINEL
            #   value: "true"
            # - name: REDIS_SENTINELS
            #   value: "redis-sentinel-1:26379,redis-sentinel-2:26379"
            # - name: REDIS_MASTER_NAME
            #   value: "mymaster"
      restartPolicy: Never
```

Apply the manifest:

```sh
kubectl apply -f stream-writer-job.yaml
```

**Scaling:**  
To scale horizontally, increase the `parallelism` field in the Job spec or use a `Deployment` for long-running workers.