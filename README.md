# AsyncJobQueue Microservices Project

A robust, production-ready microservices system for asynchronous job processing, featuring FastAPI, PostgreSQL, Redis, and modular task generation.

---

## Project Overview

This project implements a scalable, containerized job queue system with two main microservices:

- **AsyncJobQueue API** (`app/`): Handles job management, processing, and status tracking.
- **Task Generator** (`task_generator/`): Continuously generates and submits diverse tasks to the job queue.

Supporting services:
- **PostgreSQL**: Persistent storage for jobs and task history.
- **Redis**: Caching and rate limiting.

All services are orchestrated using Docker Compose for easy local development and deployment.

---

## Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌───────────────┐
│   Task Generator    │───▶│   AsyncJobQueue API │───▶│  PostgreSQL   │
│   (Port 8001)       │    │   (Port 8000)       │    │  (Port 5433)  │
└─────────────────────┘    └─────────────────────┘    └───────────────┘
         │                           │
         ▼                           ▼
┌─────────────────────┐    ┌─────────────────────┐
│   Redis Cache       │    │   Health Checks     │
│   (Port 6379)       │    │   & Monitoring      │
└─────────────────────┘    └─────────────────────┘
```

---

## Application Running Details

### 1. Start All Services

```bash
docker-compose up --build
```
- This command builds and starts all containers: PostgreSQL, Redis, AsyncJobQueue API, and Task Generator.
- The first run may take a few minutes as images are built and dependencies installed.

### 2. Monitor Service Status

- **Check running containers:**
  ```bash
  docker-compose ps
  ```
- **View logs for all services:**
  ```bash
  docker-compose logs -f
  ```
- **View logs for a specific service:**
  ```bash
  docker-compose logs -f app
  docker-compose logs -f task-generator
  docker-compose logs -f postgres
  docker-compose logs -f redis
  ```

### 3. Access Application Endpoints

- **Main API:** [http://localhost:8000](http://localhost:8000)
- **Task Generator:** [http://localhost:8001](http://localhost:8001)
- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Checks:**
  - Main API: [http://localhost:8000/health](http://localhost:8000/health)
  - Task Generator: [http://localhost:8001/health](http://localhost:8001/health)

### 4. Interact with the Application

- **Submit a job:**
  ```bash
  curl -X POST "http://localhost:8000/jobs/" \
    -H "Content-Type: application/json" \
    -d '{
      "task_type": "http_request",
      "payload": {"url": "https://jsonplaceholder.typicode.com/posts/1", "method": "GET"},
      "priority": "normal"
    }'
  ```
- **Check job status:**
  ```bash
  curl "http://localhost:8000/jobs/{job_id}"
  ```
- **Generate a single task from the generator:**
  ```bash
  curl -X POST "http://localhost:8001/generate-single"
  ```
- **Generate a batch of tasks:**
  ```bash
  curl -X POST "http://localhost:8001/generate-batch/5"
  ```

### 5. Stopping and Restarting

- **Stop all services:**
  ```bash
  docker-compose down
  ```
- **Restart all services:**
  ```bash
  docker-compose up --build
  ```
- **Remove all containers, networks, and volumes:**
  ```bash
  docker-compose down -v --rmi all
  ```

### 6. Troubleshooting

- **Check health endpoints:**
  - [http://localhost:8000/health](http://localhost:8000/health)
  - [http://localhost:8001/health](http://localhost:8001/health)
- **Check logs for errors:**
  ```bash
  docker-compose logs -f
  ```
- **Check port conflicts:**
  - PostgreSQL uses port 5433 (not 5432) to avoid local conflicts.

---

## Services

### 1. AsyncJobQueue API (`app/`)
- FastAPI-based job queue and processor
- RESTful API for job submission, status, and results
- Persistent storage in PostgreSQL
- Real-time status and health monitoring
- See [`app/README.md`](app/README.md) for details

### 2. Task Generator (`task_generator/`)
- Microservice for automated, intelligent task generation
- Supports multiple task types and priorities
- Monitors processor health and adapts behavior
- See [`task_generator/README.md`](task_generator/README.md) for details

### 3. PostgreSQL
- Stores all job and task history
- Exposed on port 5433 (to avoid local conflicts)

### 4. Redis
- Used for caching and rate limiting
- Exposed on port 6379

---

## Quick Start

### Prerequisites
- Docker Desktop (with Compose)
- At least 2GB RAM

### 1. Clone the repository
```bash
cd fastapi-practice
```

### 2. Build and start all services
```bash
docker-compose up --build
```

### 3. Access the services
- Main API: [http://localhost:8000](http://localhost:8000)
- Task Generator: [http://localhost:8001](http://localhost:8001)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Health Checks & Monitoring
- Main API: `GET /health`
- Task Generator: `GET /health`
- All services have Docker health checks and will restart on failure.

---

## Configuration

All configuration is via environment variables (see each service's README for details). Example variables:

- `DATABASE_URL` (for both services)
- `REDIS_URL`
- `TASK_PROCESSOR_URL` (for task generator)
- `GENERATION_INTERVAL`, `MAX_CONCURRENT_TASKS`, etc.

---

## Development

- Each service can be run and developed independently.
- See [`app/README.md`](app/README.md) and [`task_generator/README.md`](task_generator/README.md) for local development instructions.
- Use Docker Compose for full integration testing.

---

## Troubleshooting

- **Port conflicts:** PostgreSQL uses 5433 by default in Docker Compose.
- **Service health:** Use `/health` endpoints and `docker-compose logs` for diagnostics.
- **Reset everything:**
  ```bash
  docker-compose down -v --rmi all
  docker-compose up --build
  ```

---

## Extending the System

- Add new microservices by creating a new directory and Dockerfile, then update `docker-compose.yml`.
- Add new job/task types by extending the models and logic in each service.
- Use environment variables for all configuration to keep services decoupled.

---

## License

This project is licensed under the MIT License.

---

## Contributors
- [Your Name Here]

---

For detailed service documentation, see:
- [`app/README.md`](app/README.md)
- [`task_generator/README.md`](task_generator/README.md)