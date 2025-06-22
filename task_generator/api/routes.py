import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse

from task_generator.models import (
    TaskRequest, TaskResponse, BatchTaskRequest, BatchTaskResponse,
    TaskGenerationConfig, TaskStats, HealthCheck, MetricsData,
    TaskType, Priority
)
from task_generator.services.task_generator import TaskGeneratorService
from task_generator.services.sender import TaskSender
from task_generator.config import settings

router = APIRouter()

# Global instances
task_generator = TaskGeneratorService()
sender: Optional[TaskSender] = None
generation_task: Optional[asyncio.Task] = None
generation_enabled = False

# Statistics tracking
stats = {
    "total_generated": 0,
    "total_sent": 0,
    "total_failed": 0,
    "total_dropped": 0,
    "start_time": datetime.utcnow(),
    "by_task_type": {task_type.value: 0 for task_type in TaskType},
    "by_priority": {priority.value: 0 for priority in Priority}
}

async def get_sender() -> TaskSender:
    """Dependency to get or create sender instance."""
    global sender
    if sender is None:
        sender = TaskSender()
        await sender.__aenter__()
    return sender

@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "running",
        "task_processor_url": settings.TASK_PROCESSOR_URL,
        "generation_enabled": generation_enabled
    }

@router.post("/generate-single", response_model=TaskResponse)
async def generate_single_task(
    background_tasks: BackgroundTasks,
    task_sender: TaskSender = Depends(get_sender)
):
    """Generate and send a single task immediately."""
    try:
        # Generate task
        task = task_generator.generate_random_task()
        stats["total_generated"] += 1
        stats["by_task_type"][task.task_type.value] += 1
        stats["by_priority"][task.priority.value] += 1
        
        # Send task
        response = await task_sender.send_task(task)
        
        if response.status.value == "sent":
            stats["total_sent"] += 1
        else:
            stats["total_failed"] += 1
        
        return response
        
    except Exception as e:
        stats["total_failed"] += 1
        raise HTTPException(status_code=500, detail=f"Failed to generate task: {str(e)}")

@router.post("/generate-batch", response_model=BatchTaskResponse)
async def generate_batch_tasks(
    request: BatchTaskRequest,
    task_sender: TaskSender = Depends(get_sender)
):
    """Generate and send multiple tasks."""
    try:
        if len(request.tasks) > settings.BATCH_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"Batch size too large. Maximum allowed: {settings.BATCH_SIZE}"
            )
        
        # Update statistics
        stats["total_generated"] += len(request.tasks)
        for task in request.tasks:
            stats["by_task_type"][task.task_type.value] += 1
            stats["by_priority"][task.priority.value] += 1
        
        # Send tasks
        responses = await task_sender.send_batch_tasks(request.tasks)
        
        # Update statistics
        successful = sum(1 for r in responses if r.status.value == "sent")
        failed = len(responses) - successful
        stats["total_sent"] += successful
        stats["total_failed"] += failed
        
        return BatchTaskResponse(
            batch_id=request.batch_id or f"batch_{int(time.time())}",
            total_tasks=len(request.tasks),
            successful_tasks=successful,
            failed_tasks=failed,
            results=responses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate batch: {str(e)}")

@router.post("/generate-by-type/{task_type}")
async def generate_task_by_type(
    task_type: TaskType,
    priority: Priority = Priority.NORMAL,
    timeout: Optional[int] = 120,
    retry_count: Optional[int] = 3,
    task_sender: TaskSender = Depends(get_sender)
):
    """Generate a specific type of task."""
    try:
        task = task_generator.generate_task_by_type(
            task_type=task_type,
            priority=priority,
            timeout=timeout,
            retry_count=retry_count
        )
        
        # Update statistics
        stats["total_generated"] += 1
        stats["by_task_type"][task.task_type.value] += 1
        stats["by_priority"][task.priority.value] += 1
        
        # Send task
        response = await task_sender.send_task(task)
        
        if response.status.value == "sent":
            stats["total_sent"] += 1
        else:
            stats["total_failed"] += 1
        
        return response
        
    except Exception as e:
        stats["total_failed"] += 1
        raise HTTPException(status_code=500, detail=f"Failed to generate task: {str(e)}")

@router.post("/stress-test/{count}")
async def stress_test(
    count: int,
    task_sender: TaskSender = Depends(get_sender)
):
    """Generate stress test tasks."""
    try:
        if count > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 tasks for stress test")
        
        tasks = task_generator.generate_stress_test_tasks(count)
        
        # Update statistics
        stats["total_generated"] += len(tasks)
        for task in tasks:
            stats["by_task_type"][task.task_type.value] += 1
            stats["by_priority"][task.priority.value] += 1
        
        # Send tasks
        responses = await task_sender.send_batch_tasks(tasks)
        
        # Update statistics
        successful = sum(1 for r in responses if r.status.value == "sent")
        failed = len(responses) - successful
        stats["total_sent"] += successful
        stats["total_failed"] += failed
        
        return {
            "message": f"Stress test completed with {count} tasks",
            "successful": successful,
            "failed": failed,
            "results": responses
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stress test failed: {str(e)}")

@router.post("/start-generation")
async def start_continuous_generation(
    config: TaskGenerationConfig,
    task_sender: TaskSender = Depends(get_sender)
):
    """Start continuous task generation."""
    global generation_task, generation_enabled
    
    if generation_enabled:
        raise HTTPException(status_code=400, detail="Generation already running")
    
    generation_enabled = True
    
    async def continuous_generation():
        """Background task for continuous generation."""
        while generation_enabled:
            try:
                # Check if we can send more tasks
                queue_size = await task_sender.check_processor_queue_size()
                if queue_size >= settings.MAX_CONCURRENT_TASKS:
                    await asyncio.sleep(10)  # Wait if queue is full
                    continue
                
                # Generate and send task
                task = task_generator.generate_random_task()
                stats["total_generated"] += 1
                stats["by_task_type"][task.task_type.value] += 1
                stats["by_priority"][task.priority.value] += 1
                
                response = await task_sender.send_task(task)
                
                if response.status.value == "sent":
                    stats["total_sent"] += 1
                else:
                    stats["total_failed"] += 1
                
                # Wait before next generation
                await asyncio.sleep(config.interval_seconds)
                
            except Exception as e:
                stats["total_failed"] += 1
                await asyncio.sleep(5)  # Wait before retry
    
    generation_task = asyncio.create_task(continuous_generation())
    
    return {
        "message": "Continuous generation started",
        "config": config.dict(),
        "interval_seconds": config.interval_seconds
    }

@router.post("/stop-generation")
async def stop_continuous_generation():
    """Stop continuous task generation."""
    global generation_task, generation_enabled
    
    if not generation_enabled:
        raise HTTPException(status_code=400, detail="Generation not running")
    
    generation_enabled = False
    
    if generation_task:
        generation_task.cancel()
        try:
            await generation_task
        except asyncio.CancelledError:
            pass
    
    return {"message": "Continuous generation stopped"}

@router.get("/stats", response_model=TaskStats)
async def get_stats():
    """Get task generation statistics."""
    uptime = (datetime.utcnow() - stats["start_time"]).total_seconds()
    
    return TaskStats(
        total_generated=stats["total_generated"],
        total_sent=stats["total_sent"],
        total_failed=stats["total_failed"],
        total_retried=0,  # Not implemented yet
        by_task_type=stats["by_task_type"],
        by_priority=stats["by_priority"],
        by_status={
            "sent": stats["total_sent"],
            "failed": stats["total_failed"],
            "dropped": stats["total_dropped"]
        },
        success_rate=(
            stats["total_sent"] / (stats["total_sent"] + stats["total_failed"])
            if (stats["total_sent"] + stats["total_failed"]) > 0 else 0
        ),
        average_response_time=0.0,  # Will be updated from sender
        last_24_hours={
            "generated": stats["total_generated"],
            "sent": stats["total_sent"],
            "failed": stats["total_failed"]
        }
    )

@router.get("/health", response_model=HealthCheck)
async def health_check(task_sender: TaskSender = Depends(get_sender)):
    """Health check endpoint."""
    uptime = (datetime.utcnow() - stats["start_time"]).total_seconds()
    
    # Check processor connectivity
    try:
        queue_size = await task_sender.check_processor_queue_size()
        processor_connected = True
    except:
        processor_connected = False
    
    return HealthCheck(
        service=settings.SERVICE_NAME,
        status="healthy" if processor_connected else "degraded",
        version=settings.SERVICE_VERSION,
        timestamp=datetime.utcnow(),
        uptime=uptime,
        task_processor_connected=processor_connected,
        database_connected=True,  # Not implemented yet
        redis_connected=True  # Not implemented yet
    )

@router.get("/metrics")
async def get_metrics(task_sender: TaskSender = Depends(get_sender)):
    """Get metrics for monitoring."""
    sender_stats = task_sender.get_stats()
    
    return MetricsData(
        tasks_generated_per_minute=stats["total_generated"] / max(1, (datetime.utcnow() - stats["start_time"]).total_seconds() / 60),
        tasks_sent_per_minute=stats["total_sent"] / max(1, (datetime.utcnow() - stats["start_time"]).total_seconds() / 60),
        success_rate=sender_stats["success_rate"],
        average_response_time=sender_stats["average_response_time"],
        active_connections=1,  # Not implemented yet
        memory_usage=0.0,  # Not implemented yet
        cpu_usage=0.0  # Not implemented yet
    )

@router.get("/queue-status")
async def get_queue_status(task_sender: TaskSender = Depends(get_sender)):
    """Get current queue status from processor."""
    try:
        queue_size = await task_sender.check_processor_queue_size()
        return {
            "queue_size": queue_size,
            "max_concurrent": settings.MAX_CONCURRENT_TASKS,
            "can_send_more": queue_size < settings.MAX_CONCURRENT_TASKS,
            "rate_limit_tokens": task_sender.rate_limit_tokens
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get queue status: {str(e)}")

@router.delete("/reset-stats")
async def reset_stats():
    """Reset all statistics."""
    global stats
    stats = {
        "total_generated": 0,
        "total_sent": 0,
        "total_failed": 0,
        "total_dropped": 0,
        "start_time": datetime.utcnow(),
        "by_task_type": {task_type.value: 0 for task_type in TaskType},
        "by_priority": {priority.value: 0 for priority in Priority}
    }
    return {"message": "Statistics reset successfully"} 