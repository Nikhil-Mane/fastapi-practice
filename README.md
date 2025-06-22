# AsyncJobQueue – Real-Time Async Task Processor

## 🚀 Overview
AsyncJobQueue is a production-style, real-time asynchronous job processing system built with FastAPI, asyncio, asyncpg, aiohttp, and aiofiles. It demonstrates modern async Python patterns for scalable background processing, API integration, and database/file I/O.

---

## ✨ Features
- **Concurrent Job Submission:** Submit jobs via HTTP, processed in the background.
- **Async Background Processing:** Jobs are handled by async workers using `asyncio.Queue`.
- **Async Database Integration:** Store and retrieve job status/results in PostgreSQL using `asyncpg`.
- **Async HTTP Requests:** Call external APIs as part of job processing with `aiohttp`.
- **Timeouts & Retries:** Robust job execution with timeouts and retry logic.
- **Controlled Concurrency:** Limit concurrent processing with `asyncio.Semaphore`.
- **Graceful Shutdown:** Clean up background tasks on server shutdown.
- **Async File Logging:** Log job status to files using `aiofiles`.
- **Metrics Endpoint:** Monitor processed jobs and server health.

---

## 🧱 Architecture
```
[Client] --> [FastAPI Async Endpoint] --> [Job Queue (asyncio.Queue)]
                                      --> [Worker Coroutines]
                                      --> [Async DB + External API]
                                      --> [Status Logging/File Output]
```

---

## 🗂️ Project Structure
```
app/
  main.py                # FastAPI app, background worker setup
  config.py              # Configuration (DB, API URLs, etc.)
  requirements.txt       # Python dependencies
  routes/
    jobs.py              # Job submission/status endpoints
  services/
    worker.py            # Async worker logic
    http_client.py       # Async HTTP client
    db.py                # Async DB access
    logger.py            # Async file logger
  models/
    job.py               # Job data model
README.md
```

---

## ⚙️ Setup & Run
1. **Clone the repo:**
   ```sh
   git clone <repo-url>
   cd fastapi-practice
   ```
2. **Install dependencies:**
   ```sh
   pip install -r app/requirements.txt
   ```
3. **Configure PostgreSQL:**
   - Update `DB_URL` in `app/config.py`.
   - Create the jobs table:
     ```sql
     CREATE TABLE job_results (
         job_id UUID PRIMARY KEY,
         status TEXT NOT NULL,
         result JSONB
     );
     ```
4. **Run the server:**
   ```sh
   uvicorn app.main:app --reload
   ```

---

## 🛠️ Usage
- **Submit a job:**
  ```http
  POST /submit
  Content-Type: application/json
  { "task": "do_something", "params": { ... } }
  ```
- **Check job status/result:**
  ```http
  GET /status/{job_id}
  ```
- **Get server metrics:**
  ```http
  GET /metrics
  ```

---

## 🧰 Tech Stack
- FastAPI – async web server
- asyncio – concurrency core
- asyncpg – async PostgreSQL
- aiohttp – async HTTP client
- aiofiles – async file writing
- uvicorn – ASGI server
- PostgreSQL – job storage

---

## 🧠 Concepts Demonstrated
- `async def` / `await` everywhere (HTTP, DB, file, tasks)
- `asyncio.Queue` for background task queue
- `asyncio.gather` for parallel API calls
- `asyncio.Semaphore` for concurrency control
- Timeout & retry logic
- Async context managers (HTTP, DB, file)
- Graceful shutdown with signal handling

---

## 🏆 Best Coding Practices

- **Separation of Concerns:** Organize code by responsibility (routes, services, models, config).
- **Type Hints:** Use type hints and Pydantic models for data validation and clarity.
- **Async Everywhere:** Use async/await for all I/O-bound operations (DB, HTTP, file, background tasks).
- **Connection Pooling:** Use asyncpg connection pools for efficient DB access.
- **Resource Cleanup:** Implement graceful shutdown for background tasks and DB connections.
- **Error Handling:** Use try/except blocks and FastAPI exception handlers for robust error management.
- **Configuration Management:** Store secrets and config in environment variables or config files, not in code.
- **Logging:** Use structured, async logging for observability (e.g., aiofiles for file logs).
- **Testing:** Write async unit and integration tests for endpoints and services.
- **Documentation:** Document endpoints and code with docstrings and OpenAPI (FastAPI auto-generates docs).
- **Security:** Validate all input, use HTTPS in production, and secure DB/API credentials.
- **Dependency Management:** Pin dependency versions in requirements.txt and use virtual environments.
- **Code Formatting:** Use tools like black, isort, and flake8 for consistent code style.

---

## 🔚 Summary
This project provides a deep, practical understanding of async Python in real-world scenarios, with production-quality architecture and best practices.