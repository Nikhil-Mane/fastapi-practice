from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
import asyncio

app = FastAPI()

# Allow CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job queue and job store
job_queue = asyncio.Queue()
jobs = {}  # job_id: {"status": str, "result": dict or None}

async def worker():
    while True:
        job_id, job_data = await job_queue.get()
        jobs[job_id]["status"] = "processing"
        # Simulate external API call and processing
        await asyncio.sleep(2)  # Simulate work
        result = {"echo": job_data}
        jobs[job_id]["status"] = "done"
        jobs[job_id]["result"] = result
        job_queue.task_done()

@app.on_event("startup")
async def startup_event():
    # Start background worker
    asyncio.create_task(worker())

@app.post("/submit")
async def submit_job(payload: dict):
    job_id = str(uuid4())
    jobs[job_id] = {"status": "queued", "result": None}
    await job_queue.put((job_id, payload))
    return {"job_id": job_id}

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return {"error": "Job not found"}
    return {"job_id": job_id, **job}

@app.get("/metrics")
async def get_metrics():
    total = len(jobs)
    done = sum(1 for j in jobs.values() if j["status"] == "done")
    processing = sum(1 for j in jobs.values() if j["status"] == "processing")
    queued = sum(1 for j in jobs.values() if j["status"] == "queued")
    return {"total_jobs": total, "done": done, "processing": processing, "queued": queued}

@app.get("/")
def read_root():
    return {"message": "AsyncJobQueue API is running"} 