from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from ..services.db import JobService
from ..models.task_provider import TaskProvider, TaskProviderResponse

router = APIRouter(prefix="/providers", tags=["Task Providers"])

class TaskProviderRegistration(BaseModel):
    """Model for task provider registration."""
    name: str
    description: str
    webhook_url: Optional[str] = None
    supported_task_types: List[str]
    rate_limit: Optional[int] = 100  # tasks per minute

class TaskSubmission(BaseModel):
    """Model for task submission from providers."""
    provider_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: str = "normal"  # high, normal, low
    timeout: Optional[int] = 300  # seconds
    retry_count: Optional[int] = 3

class TaskProviderStatus(BaseModel):
    """Model for task provider status."""
    provider_id: str
    name: str
    status: str  # active, inactive, suspended
    total_tasks_submitted: int
    successful_tasks: int
    failed_tasks: int
    last_activity: datetime

# In-memory storage for providers (in production, use database)
task_providers = {}

@router.post("/register", response_model=TaskProviderResponse)
async def register_provider(registration: TaskProviderRegistration):
    """Register a new task provider."""
    try:
        provider_id = f"provider_{len(task_providers) + 1}"
        
        provider = TaskProvider(
            id=provider_id,
            name=registration.name,
            description=registration.description,
            webhook_url=registration.webhook_url,
            supported_task_types=registration.supported_task_types,
            rate_limit=registration.rate_limit,
            status="active",
            created_at=datetime.utcnow()
        )
        
        task_providers[provider_id] = provider
        
        return TaskProviderResponse(
            provider_id=provider_id,
            name=provider.name,
            status=provider.status,
            message="Provider registered successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register provider: {str(e)}")

@router.post("/{provider_id}/submit-task")
async def submit_task(provider_id: str, task: TaskSubmission, req: Request):
    """Submit a task from a provider."""
    try:
        # Validate provider
        if provider_id not in task_providers:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        provider = task_providers[provider_id]
        if provider.status != "active":
            raise HTTPException(status_code=403, detail="Provider is not active")
        
        # Validate task type
        if task.task_type not in provider.supported_task_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Task type '{task.task_type}' not supported by this provider"
            )
        
        # Create job in database
        job_id = await JobService.create_job_with_provider(
            job_id=str(uuid4()),
            task_type=task.task_type,
            payload=task.payload,
            provider_id=provider_id,
            priority=task.priority,
            timeout=task.timeout,
            retry_count=task.retry_count
        )
        
        # Add to processing queue
        await req.app.state.job_queue.put((
            job_id, 
            task.task_type, 
            task.payload,
            task.priority
        ))
        
        # Update provider stats
        provider.total_tasks_submitted += 1
        provider.last_activity = datetime.utcnow()
        
        return {
            "job_id": job_id,
            "provider_id": provider_id,
            "status": "queued",
            "message": "Task submitted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit task: {str(e)}")

@router.get("/{provider_id}/status", response_model=TaskProviderStatus)
async def get_provider_status(provider_id: str):
    """Get status of a task provider."""
    try:
        if provider_id not in task_providers:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        provider = task_providers[provider_id]
        
        # Get provider statistics from database
        stats = await JobService.get_provider_stats(provider_id)
        
        return TaskProviderStatus(
            provider_id=provider_id,
            name=provider.name,
            status=provider.status,
            total_tasks_submitted=stats.get("total", 0),
            successful_tasks=stats.get("successful", 0),
            failed_tasks=stats.get("failed", 0),
            last_activity=provider.last_activity
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get provider status: {str(e)}")

@router.get("/", response_model=List[TaskProviderStatus])
async def list_providers():
    """List all registered task providers."""
    try:
        providers = []
        for provider_id, provider in task_providers.items():
            stats = await JobService.get_provider_stats(provider_id)
            providers.append(TaskProviderStatus(
                provider_id=provider_id,
                name=provider.name,
                status=provider.status,
                total_tasks_submitted=stats.get("total", 0),
                successful_tasks=stats.get("successful", 0),
                failed_tasks=stats.get("failed", 0),
                last_activity=provider.last_activity
            ))
        return providers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list providers: {str(e)}")

@router.put("/{provider_id}/status")
async def update_provider_status(provider_id: str, status: str):
    """Update provider status (active, inactive, suspended)."""
    try:
        if provider_id not in task_providers:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        if status not in ["active", "inactive", "suspended"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        task_providers[provider_id].status = status
        task_providers[provider_id].last_activity = datetime.utcnow()
        
        return {
            "provider_id": provider_id,
            "status": status,
            "message": "Provider status updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update provider status: {str(e)}")

@router.delete("/{provider_id}")
async def unregister_provider(provider_id: str):
    """Unregister a task provider."""
    try:
        if provider_id not in task_providers:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        del task_providers[provider_id]
        
        return {
            "provider_id": provider_id,
            "message": "Provider unregistered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unregister provider: {str(e)}") 