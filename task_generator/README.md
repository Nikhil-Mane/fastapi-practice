# Task Generator Microservice

An intelligent task generation service that automatically creates and submits various types of jobs to the AsyncJobQueue system.

## Overview

The Task Generator microservice is responsible for automatically generating and submitting tasks to the main job processing system. It operates independently while maintaining awareness of the processor's health and capacity, ensuring optimal task distribution and system stability.

## Features

- **Automated Task Generation**: Continuously generates tasks at configurable intervals
- **Multiple Task Types**: Supports HTTP requests, math calculations, file operations, and data transformations
- **Intelligent Scheduling**: Adapts to processor health and capacity
- **Rate Limiting**: Prevents system overload with configurable limits
- **Health Monitoring**: Monitors processor health and adjusts behavior accordingly
- **Batch Processing**: Support for generating multiple tasks at once
- **Priority Distribution**: Generates tasks with different priority levels
- **Service Independence**: Can operate independently with graceful degradation

## Architecture

```
┌─────────────────────┐    ┌─────────────────────┐
│   Task Generator    │    │   AsyncJobQueue     │
│   (Port 8001)       │───▶│   API (Port 8000)   │
│                     │    │                     │
│   • Task Creation   │    │   • Job Processing  │
│   • Health Checks   │    │   • Status Tracking │
│   • Rate Limiting   │    │   • Result Storage  │
└─────────────────────┘    └─────────────────────┘
         │                           │
         ▼                           ▼
┌─────────────────────┐    ┌─────────────────────┐
│   PostgreSQL        │    │   Redis Cache       │
│   (Task History)    │    │   (Rate Limiting)   │
└─────────────────────┘    └─────────────────────┘
```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Service status and configuration |
| `GET` | `/health` | Health check with processor status |
| `GET` | `/stats` | Service statistics and configuration |

### Task Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/generate-single` | Generate and submit a single task |
| `POST` | `/generate-batch/{count}` | Generate and submit multiple tasks |

## Task Types

### 1. HTTP Request Tasks
Generates HTTP requests to various external APIs:

```json
{
  "task_type": "http_request",
  "payload": {
    "url": "https://jsonplaceholder.typicode.com/posts/1",
    "method": "GET",
    "headers": {"User-Agent": "TaskGenerator/1.0"},
    "timeout": 30
  },
  "priority": "normal"
}
```

**Supported Endpoints:**
- JSONPlaceholder API
- GitHub API
- HTTPBin
- Public APIs
- Dog API

### 2. Math Calculation Tasks
Generates various mathematical operations:

```json
{
  "task_type": "math_calculation",
  "payload": {
    "operation": "factorial",
    "number": 10
  },
  "priority": "high"
}
```

**Supported Operations:**
- Addition with multiple numbers
- Multiplication
- Factorial calculation
- Fibonacci sequence
- Prime number checking

### 3. File Operation Tasks
Generates file system operations:

```json
{
  "task_type": "file_operation",
  "payload": {
    "operation": "write",
    "filename": "output.txt",
    "content": "Generated content"
  },
  "priority": "low"
}
```

**Supported Operations:**
- File reading
- File writing
- File appending
- File deletion

### 4. Data Transformation Tasks
Generates data format conversions:

```json
{
  "task_type": "data_transformation",
  "payload": {
    "operation": "json_to_csv",
    "data": {"name": "John", "age": 30, "city": "NYC"}
  },
  "priority": "normal"
}
```

**Supported Transformations:**
- JSON to CSV conversion
- CSV to JSON conversion
- XML to JSON conversion
- Data filtering operations

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TASK_PROCESSOR_URL` | `http://localhost:8000` | URL of the main job processor |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:password@postgres:5432/taskgenerator` | Database connection string |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection string |
| `GENERATION_INTERVAL` | `5` | Seconds between task generations |
| `MAX_CONCURRENT_TASKS` | `10` | Maximum tasks per batch |
| `TASK_PROCESSOR_TIMEOUT` | `30` | Timeout for processor requests |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |

### Task Type Weights

```python
TASK_TYPE_WEIGHTS = {
    "http_request": 0.3,        # 30% of tasks
    "math_calculation": 0.25,   # 25% of tasks
    "file_operation": 0.25,     # 25% of tasks
    "data_transformation": 0.2  # 20% of tasks
}
```

### Priority Distribution

```python
PRIORITY_WEIGHTS = {
    "high": 0.2,    # 20% high priority
    "normal": 0.6,  # 60% normal priority
    "low": 0.2      # 20% low priority
}
```

## Development

### Local Development Setup

1. **Install dependencies:**
   ```bash
   cd task_generator
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   export TASK_PROCESSOR_URL="http://localhost:8000"
   export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/taskgenerator"
   export REDIS_URL="redis://localhost:6379/0"
   export DEBUG=true
   ```

3. **Run the service:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build task-generator

# Run in development mode
docker-compose -f docker-compose.dev.yml up task-generator
```

## Health Monitoring

### Health Check Response

```json
{
  "status": "healthy",
  "service": "Task Generator Microservice",
  "processor_connected": true,
  "timestamp": 1640995200.0
}
```

**Status Values:**
- `healthy`: Service is fully operational
- `degraded`: Service is running but processor is unavailable
- `unhealthy`: Service has critical issues

### Service Statistics

```json
{
  "supported_task_types": ["http_request", "math_calculation", "file_operation", "data_transformation"],
  "generation_interval": 5,
  "max_concurrent_tasks": 10,
  "task_processor_url": "http://app:8000",
  "service_version": "1.0.0"
}
```

## Intelligent Behavior

### Processor Health Awareness

The service continuously monitors the processor's health:

1. **Health Check**: Before sending tasks, checks processor health
2. **Graceful Degradation**: If processor is unavailable, pauses task generation
3. **Automatic Recovery**: Resumes task generation when processor becomes healthy
4. **Error Handling**: Logs warnings when processor is unavailable

### Rate Limiting

- Configurable generation intervals
- Maximum concurrent task limits
- Redis-based rate limiting
- Automatic backoff on errors

### Task Distribution

- Weighted random selection of task types
- Balanced priority distribution
- Varied payload generation
- Realistic task parameters

## Error Handling

### Common Scenarios

1. **Processor Unavailable**
   - Logs warning messages
   - Continues monitoring
   - Resumes when processor is healthy

2. **Network Issues**
   - Retry with exponential backoff
   - Timeout handling
   - Connection error logging

3. **Configuration Errors**
   - Validation of environment variables
   - Default value fallbacks
   - Startup error reporting

## Monitoring and Logging

### Log Levels

- `DEBUG`: Detailed task generation information
- `INFO`: General service operation
- `WARNING`: Processor health issues
- `ERROR`: Critical service failures

### Key Metrics

- Tasks generated per minute
- Success/failure rates
- Processor response times
- Service uptime
- Error frequency

## API Examples

### Generate Single Task

```bash
curl -X POST "http://localhost:8001/generate-single" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "message": "Task generation started",
  "task": {
    "task_type": "http_request",
    "payload": {
      "url": "https://jsonplaceholder.typicode.com/posts/1",
      "method": "GET"
    },
    "priority": "normal"
  }
}
```

### Generate Batch Tasks

```bash
curl -X POST "http://localhost:8001/generate-batch/5" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "message": "Batch task generation started for 5 tasks",
  "tasks": [
    {
      "task_type": "math_calculation",
      "payload": {"operation": "factorial", "number": 10},
      "priority": "high"
    },
    // ... more tasks
  ]
}
```

### Check Service Health

```bash
curl "http://localhost:8001/health"
```

### Get Service Statistics

```bash
curl "http://localhost:8001/stats"
```

## Troubleshooting

### Common Issues

1. **Processor Connection Failed**
   ```bash
   # Check processor health
   curl http://localhost:8000/health
   
   # Check service logs
   docker-compose logs task-generator
   ```

2. **No Tasks Being Generated**
   ```bash
   # Check if processor is healthy
   curl http://localhost:8001/health
   
   # Check generation interval
   curl http://localhost:8001/stats
   ```

3. **High Error Rate**
   ```bash
   # Check processor logs
   docker-compose logs app
   
   # Check network connectivity
   docker-compose exec task-generator ping app
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG=true
docker-compose up task-generator
```

## Performance Optimization

### Configuration Tuning

1. **Generation Interval**: Adjust based on processor capacity
2. **Batch Size**: Optimize for throughput vs. latency
3. **Worker Count**: Scale based on task complexity
4. **Timeout Values**: Balance reliability vs. responsiveness

### Resource Management

- Connection pooling for HTTP requests
- Efficient task generation algorithms
- Memory-conscious payload generation
- Optimized database queries

## Security Considerations

- Input validation for all generated tasks
- Secure communication with processor
- Environment variable protection
- Rate limiting to prevent abuse
- Error message sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add new task types or improve existing ones
4. Update tests and documentation
5. Submit a pull request

## License

This project is licensed under the MIT License. 