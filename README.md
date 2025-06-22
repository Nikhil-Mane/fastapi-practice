# AsyncJobQueue API

A FastAPI-based asynchronous job queue system with persistent database storage, supporting various types of real-world tasks.

## 🚀 Features

- **Persistent Storage**: PostgreSQL database for job persistence
- **Multiple Task Types**: HTTP requests, calculations, file operations, data transformations
- **Real-time Processing**: Asynchronous job processing with background workers
- **RESTful API**: Complete REST API for job management
- **Error Handling**: Comprehensive error handling and logging
- **Metrics**: Real-time job metrics and statistics
- **Pagination**: Support for large job lists with pagination

## 🛠️ Task Types Supported

### 1. HTTP Requests
```json
{
  "task_type": "http_request",
  "payload": {
    "method": "GET",
    "url": "https://api.github.com/users/octocat",
    "headers": {"User-Agent": "JobQueue/1.0"}
  }
}
```

### 2. Mathematical Calculations
```json
{
  "task_type": "calculation",
  "payload": {
    "operation": "sum",
    "numbers": [1, 2, 3, 4, 5]
  }
}
```

### 3. File Operations
```json
{
  "task_type": "file_operation",
  "payload": {
    "operation": "write",
    "filename": "output.txt",
    "content": "Hello World!"
  }
}
```

### 4. Data Transformations
```json
{
  "task_type": "data_transformation",
  "payload": {
    "transform_type": "uppercase",
    "data": "hello world"
  }
}
```

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+ (or Docker for automatic setup)
- pip

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
   cd fastapi-practice
   ```

### 2. Install Dependencies

```bash
cd app
pip install -r requirements.txt
```

### 3. Run the Application

```bash
uvicorn main:app --reload
```

The application will automatically:
- Start PostgreSQL in Docker (if Docker is running)
- Create database tables
- Start background workers
- Be ready to accept jobs

## 📚 API Endpoints

### Job Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/submit` | Submit a new job |
| `GET` | `/status/{job_id}` | Get job status and result |
| `GET` | `/jobs` | Get all jobs (with pagination) |
| `GET` | `/jobs/{status}` | Get jobs by status |
| `DELETE` | `/jobs/{job_id}` | Delete a job |
| `GET` | `/metrics` | Get system metrics |

## 📝 Sample Jobs

### HTTP Request Jobs

**GET Request:**
```json
{
  "task_type": "http_request",
  "payload": {
    "method": "GET",
    "url": "https://jsonplaceholder.typicode.com/posts/1",
    "headers": {
      "User-Agent": "JobQueue/1.0"
    }
  }
}
```

**POST Request:**
```json
{
  "task_type": "http_request",
  "payload": {
    "method": "POST",
    "url": "https://jsonplaceholder.typicode.com/posts",
    "headers": {
      "Content-Type": "application/json"
    },
    "data": {
      "title": "Test Post",
      "body": "This is a test post from job queue",
      "userId": 1
    }
  }
}
```

### Calculation Jobs

**Sum Calculation:**
```json
{
  "task_type": "calculation",
  "payload": {
    "operation": "sum",
    "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
  }
}
```

**Average Calculation:**
```json
{
  "task_type": "calculation",
  "payload": {
    "operation": "average",
    "numbers": [10, 20, 30, 40, 50]
  }
}
```

**Multiplication:**
```json
{
  "task_type": "calculation",
  "payload": {
    "operation": "multiply",
    "numbers": [2, 3, 4, 5]
  }
}
```

**Find Maximum:**
```json
{
  "task_type": "calculation",
  "payload": {
    "operation": "max",
    "numbers": [15, 7, 23, 9, 42, 3, 18]
  }
}
```

**Find Minimum:**
```json
{
  "task_type": "calculation",
  "payload": {
    "operation": "min",
    "numbers": [15, 7, 23, 9, 42, 3, 18]
  }
}
```

### File Operation Jobs

**Write File:**
```json
{
  "task_type": "file_operation",
  "payload": {
    "operation": "write",
    "filename": "hello.txt",
    "content": "Hello from the AsyncJobQueue!\nThis is a test file.\nTimestamp: 2024-01-15"
  }
}
```

**Read File:**
```json
{
  "task_type": "file_operation",
  "payload": {
    "operation": "read",
    "filename": "hello.txt"
  }
}
```

### Data Transformation Jobs

**Reverse String:**
```json
{
  "task_type": "data_transformation",
  "payload": {
    "transform_type": "reverse",
    "data": "Hello World!"
  }
}
```

**Convert to Uppercase:**
```json
{
  "task_type": "data_transformation",
  "payload": {
    "transform_type": "uppercase",
    "data": "hello world"
  }
}
```

**Convert to Lowercase:**
```json
{
  "task_type": "data_transformation",
  "payload": {
    "transform_type": "lowercase",
    "data": "HELLO WORLD"
  }
}
```

**Generate MD5 Hash:**
```json
{
  "task_type": "data_transformation",
  "payload": {
    "transform_type": "hash",
    "data": "password123"
  }
}
```

**Reverse Array:**
```json
{
  "task_type": "data_transformation",
  "payload": {
    "transform_type": "reverse",
    "data": ["apple", "banana", "cherry", "date"]
  }
}
```

### Echo Job (Default)
```json
{
  "task_type": "echo",
  "payload": {
    "message": "Hello from job queue",
    "timestamp": "2024-01-15T10:30:00Z",
    "data": {
      "key1": "value1",
      "key2": "value2"
    }
  }
}
```

## 📡 How to Submit Jobs

### Using curl:
```bash
# Submit a calculation job
curl -X POST "http://localhost:8000/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "calculation",
    "payload": {
      "operation": "sum",
      "numbers": [1, 2, 3, 4, 5]
    }
  }'
```

### Using Python requests:
```python
import requests

job_data = {
    "task_type": "http_request",
    "payload": {
        "method": "GET",
        "url": "https://api.github.com/users/octocat"
    }
}

response = requests.post("http://localhost:8000/submit", json=job_data)
job_id = response.json()["job_id"]
print(f"Job submitted: {job_id}")
```

### Check Job Status:
```bash
curl "http://localhost:8000/status/{job_id}"
```

## 🎯 Expected Responses

### Job Submission Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "task_type": "calculation",
  "message": "Job submitted successfully"
}
```

### Job Status Response (Done):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "done",
  "task_type": "calculation",
  "payload": {
    "operation": "sum",
    "numbers": [1, 2, 3, 4, 5]
  },
  "result": {
    "result": 15,
    "operation": "sum",
    "numbers": [1, 2, 3, 4, 5]
  },
  "error": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:05Z",
  "completed_at": "2024-01-15T10:30:05Z"
}
```

### Job Status Response (Failed):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "task_type": "http_request",
  "payload": {
    "method": "GET",
    "url": "https://invalid-url.com"
  },
  "result": null,
  "error": "Connection timeout",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:05Z",
  "completed_at": "2024-01-15T10:30:05Z"
}
```

## 🗄️ Database Schema

```sql
CREATE TABLE jobs (
    id VARCHAR PRIMARY KEY,
    status VARCHAR NOT NULL DEFAULT 'queued',
    task_type VARCHAR NOT NULL DEFAULT 'echo',
    payload JSON NOT NULL,
    result JSON,
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `5432` | Database port |
| `DB_NAME` | `asyncjobqueue` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | `password` | Database password |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_WORKERS` | `1` | Number of worker processes |
| `JOB_TIMEOUT` | `300` | Job timeout in seconds |
| `CLEANUP_DAYS` | `30` | Days to keep old jobs |

## 📊 Job Statuses

- **queued**: Job is waiting to be processed
- **processing**: Job is currently being processed
- **done**: Job completed successfully
- **failed**: Job failed with an error

## 🛡️ Error Handling

The system includes comprehensive error handling:

- **Input Validation**: Validates job payloads before processing
- **Database Errors**: Handles database connection issues gracefully
- **Task Errors**: Captures and stores task execution errors
- **HTTP Errors**: Proper error responses with status codes

## 📈 Monitoring

### Metrics Endpoint
```bash
  GET /metrics
  ```

Returns:
```json
{
  "total_jobs": 100,
  "done": 85,
  "processing": 5,
  "queued": 8,
  "failed": 2
}
```

### Logging
The application logs all operations to help with debugging and monitoring.

## 🔄 Background Processing

Jobs are processed asynchronously by background workers:

1. Job is submitted and stored in database
2. Job is added to processing queue
3. Worker picks up job and updates status to "processing"
4. Job is executed based on task type
5. Result is stored and status updated to "done" or "failed"

## 🧪 Testing

### Interactive API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

### Sample Test Script
```python
import asyncio
import aiohttp
import json

async def test_job_queue():
    async with aiohttp.ClientSession() as session:
        # Submit a calculation job
        payload = {
            "task_type": "calculation",
            "payload": {
                "operation": "sum",
                "numbers": [1, 2, 3, 4, 5]
            }
        }
        
        async with session.post("http://localhost:8000/submit", json=payload) as response:
            result = await response.json()
            job_id = result["job_id"]
            print(f"Submitted job: {job_id}")
        
        # Wait and check status
        await asyncio.sleep(3)
        
        async with session.get(f"http://localhost:8000/status/{job_id}") as response:
            status = await response.json()
            print(f"Job status: {status}")

# Run test
asyncio.run(test_job_queue())
```

## 🚀 Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production
```bash
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=asyncjobqueue
DB_USER=your-db-user
DB_PASSWORD=your-secure-password
LOG_LEVEL=WARNING
MAX_WORKERS=4
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the logs for error messages
2. Verify database connectivity
3. Ensure all dependencies are installed
4. Check the API documentation at `/docs`