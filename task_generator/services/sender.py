import asyncio
import aiohttp
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from collections import deque

from ..models import TaskRequest, TaskResponse, TaskStatus
from ..config import settings

logger = logging.getLogger(__name__)

@dataclass
class SenderStats:
    """Statistics for task sender."""
    total_sent: int = 0
    total_failed: int = 0
    total_retried: int = 0
    total_dropped: int = 0
    last_success: Optional[datetime] = None
    last_error: Optional[datetime] = None
    average_response_time: float = 0.0

class TaskSender:
    """Service for sending tasks to the processor with rate limiting and queue monitoring."""
    
    def __init__(self):
        self.stats = SenderStats()
        self.rate_limit_tokens = settings.RATE_LIMIT_PER_MINUTE
        self.last_token_reset = time.time()
        self.response_times = deque(maxlen=100)  # Keep last 100 response times
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.TASK_PROCESSOR_TIMEOUT)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def check_processor_queue_size(self) -> int:
        """Check the current queue size in the processor."""
        try:
            if not self.session:
                return 0
                
            async with self.session.get(f"{settings.TASK_PROCESSOR_URL}/jobs/queue-size") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("queue_size", 0)
                else:
                    logger.warning(f"Failed to get queue size: {response.status}")
                    return 0
        except Exception as e:
            logger.error(f"Error checking queue size: {e}")
            return 0
    
    def _can_send_task(self) -> bool:
        """Check if we can send a task based on rate limiting."""
        current_time = time.time()
        
        # Reset tokens every minute
        if current_time - self.last_token_reset >= 60:
            self.rate_limit_tokens = settings.RATE_LIMIT_PER_MINUTE
            self.last_token_reset = current_time
        
        return self.rate_limit_tokens > 0
    
    def _consume_token(self):
        """Consume a rate limit token."""
        self.rate_limit_tokens -= 1
    
    async def send_task(self, task: TaskRequest) -> TaskResponse:
        """Send a single task to the processor."""
        start_time = time.time()
        task_id = f"task_{int(start_time * 1000)}"
        
        try:
            # Check rate limiting
            if not self._can_send_task():
                self.stats.total_dropped += 1
                return TaskResponse(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    message="Rate limit exceeded"
                )
            
            # Check queue size
            queue_size = await self.check_processor_queue_size()
            if queue_size >= settings.MAX_CONCURRENT_TASKS:
                self.stats.total_dropped += 1
                return TaskResponse(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    message=f"Processor queue full ({queue_size} tasks)"
                )
            
            # Send task
            if not self.session:
                raise Exception("Session not initialized")
            
            payload = {
                "task_type": task.task_type.value,
                "payload": task.payload,
                "priority": task.priority.value,
                "timeout": task.timeout,
                "retry_count": task.retry_count
            }
            
            async with self.session.post(
                f"{settings.TASK_PROCESSOR_URL}/jobs/",
                json=payload
            ) as response:
                response_time = time.time() - start_time
                self.response_times.append(response_time)
                
                if response.status == 200:
                    result = await response.json()
                    self.stats.total_sent += 1
                    self.stats.last_success = datetime.utcnow()
                    self._consume_token()
                    
                    # Update average response time
                    self.stats.average_response_time = sum(self.response_times) / len(self.response_times)
                    
                    return TaskResponse(
                        task_id=task_id,
                        job_id=result.get("job_id"),
                        status=TaskStatus.SENT,
                        message="Task sent successfully"
                    )
                else:
                    error_text = await response.text()
                    self.stats.total_failed += 1
                    self.stats.last_error = datetime.utcnow()
                    
                    return TaskResponse(
                        task_id=task_id,
                        status=TaskStatus.FAILED,
                        message=f"HTTP {response.status}: {error_text}"
                    )
                    
        except Exception as e:
            response_time = time.time() - start_time
            self.stats.total_failed += 1
            self.stats.last_error = datetime.utcnow()
            
            logger.error(f"Error sending task: {e}")
            return TaskResponse(
                task_id=task_id,
                status=TaskStatus.FAILED,
                message=f"Exception: {str(e)}"
            )
    
    async def send_batch_tasks(self, tasks: List[TaskRequest]) -> List[TaskResponse]:
        """Send multiple tasks with concurrency control."""
        semaphore = asyncio.Semaphore(10)  # Max 10 concurrent requests
        
        async def send_with_semaphore(task: TaskRequest) -> TaskResponse:
            async with semaphore:
                return await self.send_task(task)
        
        # Send tasks concurrently
        results = await asyncio.gather(
            *[send_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )
        
        # Convert exceptions to failed responses
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(TaskResponse(
                    task_id=f"task_batch_{i}",
                    status=TaskStatus.FAILED,
                    message=f"Exception: {str(result)}"
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current sender statistics."""
        return {
            "total_sent": self.stats.total_sent,
            "total_failed": self.stats.total_failed,
            "total_retried": self.stats.total_retried,
            "total_dropped": self.stats.total_dropped,
            "success_rate": (
                self.stats.total_sent / (self.stats.total_sent + self.stats.total_failed)
                if (self.stats.total_sent + self.stats.total_failed) > 0 else 0
            ),
            "average_response_time": self.stats.average_response_time,
            "rate_limit_tokens_remaining": self.rate_limit_tokens,
            "last_success": self.stats.last_success.isoformat() if self.stats.last_success else None,
            "last_error": self.stats.last_error.isoformat() if self.stats.last_error else None
        } 