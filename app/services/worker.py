import asyncio
import aiohttp
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from app.services.db import JobService

# Setup logging
logger = logging.getLogger(__name__)

class JobProcessor:
    """Job processor for handling different types of tasks."""
    
    @staticmethod
    async def process_http_request(job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process HTTP request tasks."""
        try:
            async with aiohttp.ClientSession() as session:
                method = job_data.get("method", "GET")
                url = job_data.get("url")
                headers = job_data.get("headers", {})
                data = job_data.get("data")
                
                if not url:
                    return {"error": "URL is required for HTTP requests"}
                
                if method.upper() == "GET":
                    async with session.get(url, headers=headers) as response:
                        content = await response.text()
                        return {
                            "status_code": response.status,
                            "headers": dict(response.headers),
                            "content": content[:1000]  # Limit content length
                        }
                elif method.upper() == "POST":
                    async with session.post(url, headers=headers, json=data) as response:
                        content = await response.text()
                        return {
                            "status_code": response.status,
                            "headers": dict(response.headers),
                            "content": content[:1000]
                        }
                else:
                    return {"error": f"Unsupported HTTP method: {method}"}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    async def process_calculation(job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process mathematical calculations."""
        try:
            operation = job_data.get("operation")
            numbers = job_data.get("numbers", [])
            
            if not operation:
                return {"error": "Operation is required for calculations"}
            
            if not isinstance(numbers, list):
                return {"error": "Numbers must be a list"}
            
            if operation == "sum":
                result = sum(numbers)
            elif operation == "average":
                result = sum(numbers) / len(numbers) if numbers else 0
            elif operation == "multiply":
                result = 1
                for num in numbers:
                    result *= num
            elif operation == "max":
                result = max(numbers) if numbers else None
            elif operation == "min":
                result = min(numbers) if numbers else None
            else:
                return {"error": f"Unknown operation: {operation}"}
                
            return {"result": result, "operation": operation, "numbers": numbers}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    async def process_file_operation(job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process file operations."""
        try:
            operation = job_data.get("operation")
            filename = job_data.get("filename")
            content = job_data.get("content", "")
            
            if not operation:
                return {"error": "Operation is required for file operations"}
            
            if not filename:
                return {"error": "Filename is required for file operations"}
            
            if operation == "write":
                # Create a unique filename to avoid conflicts
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_filename = f"job_output_{timestamp}_{filename}"
                
                with open(unique_filename, "w") as f:
                    f.write(content)
                
                return {
                    "message": "File written successfully",
                    "filename": unique_filename,
                    "size": len(content)
                }
                
            elif operation == "read":
                if os.path.exists(filename):
                    with open(filename, "r") as f:
                        content = f.read()
                    return {
                        "content": content[:1000],  # Limit content length
                        "size": len(content)
                    }
                else:
                    return {"error": f"File {filename} not found"}
            else:
                return {"error": f"Unknown file operation: {operation}"}
                    
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    async def process_data_transformation(job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data transformation tasks."""
        try:
            data = job_data.get("data", [])
            transform_type = job_data.get("transform_type")
            
            if not transform_type:
                return {"error": "Transform type is required for data transformations"}
            
            if transform_type == "reverse":
                if isinstance(data, list):
                    result = data[::-1]
                elif isinstance(data, str):
                    result = data[::-1]
                else:
                    result = str(data)[::-1]
                    
            elif transform_type == "uppercase":
                if isinstance(data, str):
                    result = data.upper()
                else:
                    result = str(data).upper()
                    
            elif transform_type == "lowercase":
                if isinstance(data, str):
                    result = data.lower()
                else:
                    result = str(data).lower()
                    
            elif transform_type == "hash":
                if isinstance(data, str):
                    result = hashlib.md5(data.encode()).hexdigest()
                else:
                    result = hashlib.md5(str(data).encode()).hexdigest()
                    
            else:
                return {"error": f"Unknown transform type: {transform_type}"}
                
            return {"original": data, "transformed": result, "transform_type": transform_type}
            
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    async def process_job(task_type: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a job based on its task type."""
        if task_type == "http_request":
            return await JobProcessor.process_http_request(job_data)
        elif task_type == "calculation":
            return await JobProcessor.process_calculation(job_data)
        elif task_type == "file_operation":
            return await JobProcessor.process_file_operation(job_data)
        elif task_type == "data_transformation":
            return await JobProcessor.process_data_transformation(job_data)
        else:
            # Default echo behavior
            return {"echo": job_data}

async def worker_loop(job_queue: asyncio.Queue):
    """Main worker loop that processes jobs from the queue."""
    logger.info("Worker started - waiting for jobs...")
    
    while True:
        try:
            # Get job from queue
            job_id, task_type, job_data = await job_queue.get()
            logger.info(f"Processing job {job_id} ({task_type})")
            
            # Update status to processing
            success = await JobService.update_job_status(job_id, "processing")
            if not success:
                logger.error(f"Failed to update job {job_id} status to processing")
                job_queue.task_done()
                continue
            
            # Process the job
            result = await JobProcessor.process_job(task_type, job_data)
            
            # Check if there was an error in the result
            if "error" in result:
                await JobService.update_job_status(job_id, "failed", error=result["error"])
                logger.error(f"Job {job_id} failed: {result['error']}")
            else:
                await JobService.update_job_status(job_id, "done", result=result)
                logger.info(f"Job {job_id} completed successfully")
                
        except Exception as e:
            logger.error(f"Worker error processing job: {e}")
            # Try to update job status to failed
            try:
                await JobService.update_job_status(job_id, "failed", error=str(e))
            except:
                pass
        finally:
            job_queue.task_done()

async def start_workers(num_workers: int = 1, job_queue: Optional[asyncio.Queue] = None):
    """Start multiple worker processes."""
    if job_queue is None:
        job_queue = asyncio.Queue()
    
    workers = []
    for i in range(num_workers):
        worker = asyncio.create_task(worker_loop(job_queue))
        workers.append(worker)
        logger.info(f"Started worker {i+1}")
    
    return workers, job_queue

async def stop_workers(workers: list):
    """Stop all worker processes."""
    for worker in workers:
        worker.cancel()
    
    # Wait for all workers to complete
    await asyncio.gather(*workers, return_exceptions=True)
    logger.info("All workers stopped") 