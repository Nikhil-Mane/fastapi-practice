# Docker Setup for AsyncJobQueue Microservices

This document provides instructions for running the AsyncJobQueue system using Docker containers.

## Architecture

The system consists of the following microservices:

- **PostgreSQL Database** (port 5432): Persistent storage for jobs and task history
- **Redis** (port 6379): Caching and rate limiting
- **Main FastAPI App** (port 8000): Job processing and management
- **Task Generator** (port 8001): Automated task generation microservice

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (usually included with Docker Desktop)
- At least 2GB of available RAM

## Quick Start

1. **Clone and navigate to the project directory:**
   ```bash
   cd fastapi-practice
   ```

2. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

3. **Access the services:**
   - Main API: http://localhost:8000
   - Task Generator: http://localhost:8001
   - API Documentation: http://localhost:8000/docs

## Service Dependencies

The services start in the following order with health checks:

1. **PostgreSQL** - Database initialization
2. **Redis** - Cache and rate limiting
3. **Main App** - Waits for PostgreSQL and Redis
4. **Task Generator** - Waits for all other services

## Health Checks

Each service includes health check endpoints:

- Main App: `GET /health`
- Task Generator: `GET /health`

Health checks verify:
- Database connectivity
- Service dependencies
- Overall service status

## Environment Variables

### Main App Environment Variables
```env
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/asyncjobqueue
REDIS_URL=redis://redis:6379/0
DEBUG=false
LOG_LEVEL=INFO
```

### Task Generator Environment Variables
```env
TASK_PROCESSOR_URL=http://app:8000
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/taskgenerator
REDIS_URL=redis://redis:6379/0
DEBUG=false
LOG_LEVEL=INFO
GENERATION_INTERVAL=5
MAX_CONCURRENT_TASKS=10
```

## API Endpoints

### Main App (Port 8000)
- `GET /` - Service status
- `GET /health` - Health check
- `GET /docs` - API documentation
- `POST /jobs/` - Create new job
- `GET /jobs/{job_id}` - Get job status
- `GET /jobs/` - List all jobs

### Task Generator (Port 8001)
- `GET /` - Service status
- `GET /health` - Health check
- `POST /generate-single` - Generate single task
- `POST /generate-batch/{count}` - Generate batch of tasks
- `GET /stats` - Service statistics

## Monitoring and Logs

### View logs for all services:
```bash
docker-compose logs -f
```

### View logs for specific service:
```bash
docker-compose logs -f app
docker-compose logs -f task-generator
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Check service status:
```bash
docker-compose ps
```

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Check if ports are in use
   netstat -an | grep :8000
   netstat -an | grep :8001
   netstat -an | grep :5432
   netstat -an | grep :6379
   ```

2. **Database connection issues:**
   ```bash
   # Check database logs
   docker-compose logs postgres
   
   # Test database connection
   docker-compose exec postgres psql -U postgres -d asyncjobqueue -c "SELECT 1;"
   ```

3. **Service dependency issues:**
   ```bash
   # Check health status
   curl http://localhost:8000/health
   curl http://localhost:8001/health
   ```

4. **Memory issues:**
   ```bash
   # Check container resource usage
   docker stats
   ```

### Reset Everything

To completely reset the system:

```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Rebuild and start
docker-compose up --build
```

## Development

### Running in Development Mode

1. **Set debug mode:**
   ```bash
   export DEBUG=true
   docker-compose up --build
   ```

2. **Mount source code for live reload:**
   ```yaml
   # Add to docker-compose.yml for development
   volumes:
     - ./app:/app
     - ./task_generator:/app
   ```

### Adding New Services

1. Create a new Dockerfile
2. Add service to docker-compose.yml
3. Update dependencies and health checks
4. Test with `docker-compose up --build`

## Production Considerations

1. **Security:**
   - Change default passwords
   - Use secrets management
   - Enable SSL/TLS
   - Restrict network access

2. **Performance:**
   - Adjust resource limits
   - Configure connection pooling
   - Enable caching
   - Monitor resource usage

3. **Monitoring:**
   - Add Prometheus metrics
   - Configure log aggregation
   - Set up alerting
   - Monitor service health

## Commands Reference

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Rebuild images
docker-compose build

# View logs
docker-compose logs

# Execute commands in containers
docker-compose exec app python -c "print('Hello')"
docker-compose exec postgres psql -U postgres -d asyncjobqueue

# Scale services
docker-compose up --scale app=3

# Clean up
docker-compose down -v --rmi all
``` 