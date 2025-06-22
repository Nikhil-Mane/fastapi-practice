from fastapi import APIRouter

router = APIRouter()

@router.post("/submit")
async def submit_job():
    # TODO: Implement job submission
    return {"message": "Job submitted"}

@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    # TODO: Implement job status check
    return {"job_id": job_id, "status": "pending"} 