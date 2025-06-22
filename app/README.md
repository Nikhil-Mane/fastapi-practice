# AsyncJobQueue API Service

A FastAPI-based asynchronous job queue system with PostgreSQL persistence and Redis caching.

## Overview

The AsyncJobQueue API service is the core component of the microservices architecture that handles job processing, management, and execution. It provides a robust, scalable solution for managing asynchronous tasks with persistent storage and real-time status tracking.

## Features

- **Asynchronous Job Processing**: Handle multiple job types concurrently
- **Persistent Storage**: PostgreSQL database for job history and status
- **Real-time Status Tracking**: Monitor job progress and results
- **Health Monitoring**: Built-in health checks and monitoring
- **RESTful API**: Comprehensive REST API with OpenAPI documentation
- **Worker Pool**: Configurable worker processes for job execution
- **Error Handling**: Robust error handling and retry mechanisms

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Task Generator│    │   AsyncJobQueue │    │   PostgreSQL    │
│   (Port 8001)   │───▶│   API (Port 8000)│───▶│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Redis Cache   │
                       │   (Port 6379)   │
                       └─────────────────┘
```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Service status and information |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/docs` | Interactive API documentation |

### Job Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/jobs/` | Create a new job |
| `GET` | `/jobs/{job_id}` | Get job status and details |
| `GET` | `/jobs/` | List all jobs with pagination |
| `DELETE` | `/jobs/{job_id}` | Delete a job |

### Job Status Values

- `queued`: Job is waiting to be processed
- `processing`: Job is currently being executed
- `done`: Job completed successfully
- `failed`: Job failed with an error

## Job Types

### 1. HTTP Request Jobs
```json
{
  "task_type": "http_request",
  "payload": {
    "url": "https://api.example.com/data",
    "method": "GET",
    "headers": {"Authorization": "Bearer token"},
    "timeout": 30
  },
  "priority": "high"
}
```

### 2. Math Calculation Jobs
```json
{
  "task_type": "math_calculation",
  "payload": {
    "operation": "factorial",
    "number": 10
  },
  "priority": "normal"
}
```

### 3. File Operation Jobs
```json
{
  "task_type": "file_operation",
  "payload": {
    "operation": "write",
    "filename": "output.txt",
    "content": "Hello World!"
  },
  "priority": "low"
}
```

### 4. Data Transformation Jobs
```json
{
  "task_type": "data_transformation",
  "payload": {
    "operation": "json_to_csv",
    "data": {"name": "John", "age": 30}
  },
  "priority": "normal"
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:password@postgres:5432/asyncjobqueue` | PostgreSQL connection string |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection string |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_WORKERS` | `1` | Number of worker processes |
| `JOB_TIMEOUT` | `300` | Job execution timeout (seconds) |

### Database Schema

```sql
CREATE TABLE jobs (
    id VARCHAR PRIMARY KEY,
    status VARCHAR NOT NULL,
    task_type VARCHAR NOT NULL,
    payload JSONB,
    result JSONB,
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);
```

## Development

### Local Development Setup

1. **Install dependencies:**
   ```bash
   cd app
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/asyncjobqueue"
   export REDIS_URL="redis://localhost:6379/0"
   export DEBUG=true
   ```

3. **Run the application:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build app

# Run in development mode with volume mounting
docker-compose -f docker-compose.dev.yml up app
```

## Monitoring and Health Checks

### Health Check Endpoint

The `/health` endpoint provides comprehensive health information:

```json
{
  "status": "healthy",
  "service": "AsyncJobQueue API",
  "database": "connected",
  "timestamp": 1640995200.0
}
```

### Logging

The service uses structured logging with the following levels:
- `DEBUG`: Detailed debugging information
- `INFO`: General information about service operation
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failed operations

### Metrics

Key metrics tracked:
- Total jobs processed
- Jobs by status (queued, processing, done, failed)
- Average job processing time
- Worker pool utilization
- Database connection status

## Error Handling

### Common Error Scenarios

1. **Database Connection Issues**
   - Automatic retry with exponential backoff
   - Graceful degradation when database is unavailable
   - Health check failures trigger service restart

2. **Job Processing Failures**
   - Detailed error logging with stack traces
   - Job status updated to "failed" with error message
   - Failed jobs can be retried manually

3. **Worker Pool Issues**
   - Automatic worker restart on failure
   - Load balancing across available workers
   - Graceful shutdown handling

## Security Considerations

- Input validation for all job payloads
- SQL injection prevention through parameterized queries
- Rate limiting to prevent abuse
- CORS configuration for web client access
- Environment variable-based configuration

## Performance Optimization

- Connection pooling for database connections
- Redis caching for frequently accessed data
- Asynchronous job processing
- Configurable worker pool size
- Database query optimization

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check database status
   docker-compose logs postgres
   
   # Test connection
   docker-compose exec postgres psql -U postgres -d asyncjobqueue -c "SELECT 1;"
   ```

2. **Service Not Starting**
   ```bash
   # Check logs
   docker-compose logs app
   
   # Check health endpoint
   curl http://localhost:8000/health
   ```

3. **Jobs Not Processing**
   ```bash
   # Check worker status
   docker-compose logs app | grep worker
   
   # Check job queue
   curl http://localhost:8000/jobs/
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG=true
docker-compose up app
```

## API Examples

### Create a Job

```bash
curl -X POST "http://localhost:8000/jobs/" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "http_request",
    "payload": {
      "url": "https://jsonplaceholder.typicode.com/posts/1",
      "method": "GET"
    },
    "priority": "normal"
  }'
```

### Get Job Status

```bash
curl "http://localhost:8000/jobs/{job_id}"
```

### List All Jobs

```bash
curl "http://localhost:8000/jobs/?limit=10&offset=0"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License. 