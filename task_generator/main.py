import asyncio
import aiohttp
import random
import time
import os
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
from .config import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.SERVICE_NAME, version=settings.SERVICE_VERSION)

class TaskRequest(BaseModel):
    """Model for task submission to processor."""
    task_type: str
    payload: Dict[str, Any]
    priority: str = "normal"

class TaskGenerator:
    """Generates various types of tasks."""
    
    def __init__(self):
        self.task_types = [
            "http_request",
            "math_calculation", 
            "file_operation",
            "data_transformation"
        ]
        
        self.http_endpoints = settings.HTTP_ENDPOINTS
        
        self.math_operations = [
            {"operation": "add", "numbers": [1, 2, 3, 4, 5]},
            {"operation": "multiply", "numbers": [2, 3, 4, 5]},
            {"operation": "factorial", "number": 10},
            {"operation": "fibonacci", "n": 20},
            {"operation": "prime_check", "number": 97}
        ]
        
        self.file_operations = [
            {"operation": "read", "filename": "sample.txt", "content": "Hello World!"},
            {"operation": "write", "filename": "output.txt", "content": "Generated content"},
            {"operation": "append", "filename": "log.txt", "content": f"Log entry at {datetime.now()}"},
            {"operation": "delete", "filename": "temp.txt"}
        ]
        
        self.data_transformations = [
            {"operation": "json_to_csv", "data": {"name": "John", "age": 30, "city": "NYC"}},
            {"operation": "csv_to_json", "data": "name,age,city\nJohn,30,NYC\nJane,25,LA"},
            {"operation": "xml_to_json", "data": "<person><name>John</name><age>30</age></person>"},
            {"operation": "data_filter", "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "condition": "even"}
        ]
    
    def generate_http_task(self) -> Dict[str, Any]:
        """Generate HTTP request task."""
        endpoint = random.choice(self.http_endpoints)
        method = random.choice(["GET", "POST"])
        
        payload = {
            "url": endpoint,
            "method": method,
            "headers": {"User-Agent": "TaskGenerator/1.0"},
            "timeout": random.randint(5, 30)
        }
        
        if method == "POST":
            payload["data"] = {"message": f"Generated at {datetime.now()}"}
        
        return payload
    
    def generate_math_task(self) -> Dict[str, Any]:
        """Generate mathematical calculation task."""
        return random.choice(self.math_operations)
    
    def generate_file_task(self) -> Dict[str, Any]:
        """Generate file operation task."""
        return random.choice(self.file_operations)
    
    def generate_data_task(self) -> Dict[str, Any]:
        """Generate data transformation task."""
        return random.choice(self.data_transformations)
    
    def generate_random_task(self) -> TaskRequest:
        """Generate a random task of any type."""
        task_type = random.choice(self.task_types)
        priority = random.choice(["high", "normal", "low"])
        
        if task_type == "http_request":
            payload = self.generate_http_task()
        elif task_type == "math_calculation":
            payload = self.generate_math_task()
        elif task_type == "file_operation":
            payload = self.generate_file_task()
        elif task_type == "data_transformation":
            payload = self.generate_data_task()
        else:
            payload = {"message": "Unknown task type"}
        
        return TaskRequest(
            task_type=task_type,
            payload=payload,
            priority=priority
        )

# Global task generator instance
task_generator = TaskGenerator()

async def check_processor_health() -> bool:
    """Check if the task processor is healthy."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{settings.TASK_PROCESSOR_URL}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
    except Exception:
        return False

async def send_task_to_processor(task: TaskRequest) -> bool:
    """Send task to the Task Processor microservice."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.TASK_PROCESSOR_URL}/submit",
                json=task.dict(),
                timeout=aiohttp.ClientTimeout(total=settings.TASK_PROCESSOR_TIMEOUT)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Task sent successfully: {result.get('job_id')}")
                    return True
                else:
                    logger.error(f"❌ Failed to send task: {response.status}")
                    return False
    except Exception as e:
        logger.error(f"❌ Error sending task: {e}")
        return False

async def continuous_task_generation():
    """Continuously generate and send tasks."""
    logger.info("🚀 Starting continuous task generation...")
    
    while True:
        try:
            # Check processor health before sending
            processor_healthy = await check_processor_health()
            
            if not processor_healthy:
                logger.warning("⚠️ Task processor is not healthy, skipping task generation")
                await asyncio.sleep(settings.GENERATION_INTERVAL)
                continue
            
            # Generate a random task
            task = task_generator.generate_random_task()
            
            # Send to processor
            success = await send_task_to_processor(task)
            
            if success:
                logger.info(f"📤 Generated and sent {task.task_type} task with {task.priority} priority")
            else:
                logger.warning(f"⚠️ Failed to send {task.task_type} task")
            
            # Wait before next generation
            await asyncio.sleep(settings.GENERATION_INTERVAL)
            
        except Exception as e:
            logger.error(f"❌ Error in task generation: {e}")
            await asyncio.sleep(settings.GENERATION_INTERVAL)

@app.on_event("startup")
async def startup_event():
    """Start task generation on startup."""
    asyncio.create_task(continuous_task_generation())

@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "running",
        "task_processor_url": settings.TASK_PROCESSOR_URL,
        "generation_interval": settings.GENERATION_INTERVAL
    }

@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint for Docker."""
    try:
        # Check processor health
        processor_healthy = await check_processor_health()
        
        return {
            "status": "healthy" if processor_healthy else "degraded",
            "service": settings.SERVICE_NAME,
            "processor_connected": processor_healthy,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/generate-single")
async def generate_single_task(background_tasks: BackgroundTasks):
    """Generate and send a single task immediately."""
    # Check processor health first
    processor_healthy = await check_processor_health()
    if not processor_healthy:
        raise HTTPException(status_code=503, detail="Task processor is not available")
    
    task = task_generator.generate_random_task()
    background_tasks.add_task(send_task_to_processor, task)
    
    return {
        "message": "Task generation started",
        "task": task.dict()
    }

@app.post("/generate-batch/{count}")
async def generate_batch_tasks(count: int, background_tasks: BackgroundTasks):
    """Generate and send multiple tasks."""
    if count > settings.MAX_CONCURRENT_TASKS:
        raise ValueError(f"Maximum {settings.MAX_CONCURRENT_TASKS} tasks allowed per batch")
    
    # Check processor health first
    processor_healthy = await check_processor_health()
    if not processor_healthy:
        raise HTTPException(status_code=503, detail="Task processor is not available")
    
    tasks = []
    for _ in range(count):
        task = task_generator.generate_random_task()
        tasks.append(task)
        background_tasks.add_task(send_task_to_processor, task)
    
    return {
        "message": f"Batch task generation started for {count} tasks",
        "tasks": [task.dict() for task in tasks]
    }

@app.get("/stats")
def get_generator_stats():
    """Get task generator statistics."""
    return {
        "supported_task_types": task_generator.task_types,
        "generation_interval": settings.GENERATION_INTERVAL,
        "max_concurrent_tasks": settings.MAX_CONCURRENT_TASKS,
        "task_processor_url": settings.TASK_PROCESSOR_URL,
        "service_version": settings.SERVICE_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT) 