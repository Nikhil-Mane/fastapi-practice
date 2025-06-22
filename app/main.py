import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .services.db import init_db, close_db
from .services.worker import start_workers, stop_workers
from .routes.jobs import router as jobs_router

logger = logging.getLogger(__name__)

async def setup_database():
    """Setup database connection using environment variables."""
    try:
        await init_db()
        logger.info("✅ Connected to database successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle events."""
    try:
        # Setup database
        db_ready = await setup_database()
        if not db_ready:
            logger.error("❌ Cannot start application without database")
            raise Exception("Database setup failed")
        
        # Create a shared job queue and start workers
        app.state.job_queue = asyncio.Queue()
        app.state.workers, _ = await start_workers(num_workers=1, job_queue=app.state.job_queue)
        logger.info("✅ Application started successfully")
        yield
    finally:
        # Stop workers and close DB
        if hasattr(app.state, 'workers'):
            await stop_workers(app.state.workers)
        await close_db()
        logger.info("✅ Application shutdown complete")

app = FastAPI(lifespan=lifespan)

# Allow CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(jobs_router)

@app.get("/")
def read_root() -> dict:
    """Root endpoint that returns a simple status message."""
    return {"message": "AsyncJobQueue API is running"}

@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint for Docker."""
    try:
        # Check database connection
        from app.services.db import get_db
        async with get_db() as db:
            await db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "service": "AsyncJobQueue API",
            "database": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")