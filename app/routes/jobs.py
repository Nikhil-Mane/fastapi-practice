"""Job routes for AsyncJobQueue."""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional
from uuid import uuid4
import asyncio

from app.services.db import JobService
from app.models.job import JobResponse

router = APIRouter()

class JobSubmissionRequest(BaseModel):
    """Request model for job submission."""
    task_type: str = "echo"
    payload: Dict[str, Any]

class JobSubmissionResponse(BaseModel):
    """Response model for job submission."""
    job_id: str
    status: str
    task_type: str
    message: str

@router.post("/submit", response_model=JobSubmissionResponse)
async def submit_job(request: JobSubmissionRequest, req: Request):
    """Submit a new job to the processing queue."""
    try:
        job_id = str(uuid4())
        
        # Create job in database
        job = await JobService.create_job(job_id, request.task_type, request.payload)
        
        # Add to processing queue via app state
        await req.app.state.job_queue.put((job_id, request.task_type, request.payload))
        
        return JobSubmissionResponse(
            job_id=job_id,
            status="queued",
            task_type=request.task_type,
            message="Job submitted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit job: {str(e)}")

@router.get("/status/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """Get the status and result of a specific job."""
    try:
        job = await JobService.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobResponse(
            id=job.id,
            status=job.status,
            task_type=job.task_type,
            payload=job.payload,
            result=job.result,
            error=job.error,
            created_at=job.created_at,
            updated_at=job.updated_at,
            completed_at=job.completed_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@router.get("/jobs")
async def get_all_jobs(limit: int = 100, offset: int = 0):
    """Get all jobs with pagination."""
    try:
        jobs = await JobService.get_all_jobs(limit=limit, offset=offset)
        return [
            JobResponse(
                id=job.id,
                status=job.status,
                task_type=job.task_type,
                payload=job.payload,
                result=job.result,
                error=job.error,
                created_at=job.created_at,
                updated_at=job.updated_at,
                completed_at=job.completed_at
            ) for job in jobs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get jobs: {str(e)}")

@router.get("/jobs/{status}")
async def get_jobs_by_status(status: str, limit: int = 100, offset: int = 0):
    """Get jobs by status with pagination."""
    try:
        valid_statuses = ["queued", "processing", "done", "failed"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        jobs = await JobService.get_jobs_by_status(status, limit=limit, offset=offset)
        return [
            JobResponse(
                id=job.id,
                status=job.status,
                task_type=job.task_type,
                payload=job.payload,
                result=job.result,
                error=job.error,
                created_at=job.created_at,
                updated_at=job.updated_at,
                completed_at=job.completed_at
            ) for job in jobs
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get jobs by status: {str(e)}")

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job by ID."""
    try:
        success = await JobService.delete_job(job_id)
        if not success:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"message": f"Job {job_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")

@router.get("/metrics")
async def get_metrics():
    """Get metrics about all jobs in the system."""
    try:
        return await JobService.get_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}") 