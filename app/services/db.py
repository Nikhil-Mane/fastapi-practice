from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import json
import logging

from app.models.job import Base, JobDB
from app.config import DB_URL

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Convert PostgreSQL URL to async version
ASYNC_DB_URL = DB_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(
    ASYNC_DB_URL, 
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300
)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def init_db():
    """Initialize database tables."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def close_db():
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")

class JobService:
    """Service for job database operations."""
    
    @staticmethod
    async def create_job(job_id: str, task_type: str, payload: Dict[str, Any]) -> JobDB:
        """Create a new job in the database."""
        try:
            async with AsyncSessionLocal() as session:
                job = JobDB(
                    id=job_id,
                    status="queued",
                    task_type=task_type,
                    payload=payload,
                    created_at=datetime.now(timezone.utc)
                )
                session.add(job)
                await session.commit()
                await session.refresh(job)
                logger.info(f"Created job {job_id} with type {task_type}")
                return job
        except Exception as e:
            logger.error(f"Failed to create job {job_id}: {e}")
            raise
    
    @staticmethod
    async def get_job(job_id: str) -> Optional[JobDB]:
        """Get a job by ID."""
        try:
            async with AsyncSessionLocal() as session:
                stmt = select(JobDB).where(JobDB.id == job_id)
                result = await session.execute(stmt)
                job = result.scalar_one_or_none()
                return job
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
    
    @staticmethod
    async def update_job_status(
        job_id: str, 
        status: str, 
        result: Optional[Dict[str, Any]] = None, 
        error: Optional[str] = None
    ) -> bool:
        """Update job status and result."""
        try:
            async with AsyncSessionLocal() as session:
                update_data = {
                    "status": status,
                    "updated_at": datetime.now(timezone.utc)
                }
                
                if result is not None:
                    update_data["result"] = result
                
                if error is not None:
                    update_data["error"] = error
                
                if status in ["done", "failed"]:
                    update_data["completed_at"] = datetime.now(timezone.utc)
                
                stmt = (
                    update(JobDB)
                    .where(JobDB.id == job_id)
                    .values(**update_data)
                )
                
                result = await session.execute(stmt)
                await session.commit()
                
                if result.rowcount > 0:
                    logger.info(f"Updated job {job_id} status to {status}")
                    return True
                else:
                    logger.warning(f"Job {job_id} not found for update")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {e}")
            return False
    
    @staticmethod
    async def get_all_jobs(limit: int = 100, offset: int = 0) -> List[JobDB]:
        """Get all jobs with pagination."""
        try:
            async with AsyncSessionLocal() as session:
                stmt = (
                    select(JobDB)
                    .order_by(JobDB.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                )
                result = await session.execute(stmt)
                jobs = result.scalars().all()
                return list(jobs)
        except Exception as e:
            logger.error(f"Failed to get all jobs: {e}")
            return []
    
    @staticmethod
    async def get_jobs_by_status(status: str, limit: int = 100, offset: int = 0) -> List[JobDB]:
        """Get jobs by status with pagination."""
        try:
            async with AsyncSessionLocal() as session:
                stmt = (
                    select(JobDB)
                    .where(JobDB.status == status)
                    .order_by(JobDB.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                )
                result = await session.execute(stmt)
                jobs = result.scalars().all()
                return list(jobs)
        except Exception as e:
            logger.error(f"Failed to get jobs by status {status}: {e}")
            return []
    
    @staticmethod
    async def get_metrics() -> Dict[str, int]:
        """Get job metrics."""
        try:
            async with AsyncSessionLocal() as session:
                # Get total count
                total_stmt = select(JobDB.id)
                total_result = await session.execute(total_stmt)
                total = len(total_result.scalars().all())
                
                # Get counts by status
                done_stmt = select(JobDB.id).where(JobDB.status == "done")
                done_result = await session.execute(done_stmt)
                done = len(done_result.scalars().all())
                
                processing_stmt = select(JobDB.id).where(JobDB.status == "processing")
                processing_result = await session.execute(processing_stmt)
                processing = len(processing_result.scalars().all())
                
                queued_stmt = select(JobDB.id).where(JobDB.status == "queued")
                queued_result = await session.execute(queued_stmt)
                queued = len(queued_result.scalars().all())
                
                failed_stmt = select(JobDB.id).where(JobDB.status == "failed")
                failed_result = await session.execute(failed_stmt)
                failed = len(failed_result.scalars().all())
                
                return {
                    "total_jobs": total,
                    "done": done,
                    "processing": processing,
                    "queued": queued,
                    "failed": failed
                }
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {
                "total_jobs": 0,
                "done": 0,
                "processing": 0,
                "queued": 0,
                "failed": 0
            }
    
    @staticmethod
    async def delete_job(job_id: str) -> bool:
        """Delete a job by ID."""
        try:
            async with AsyncSessionLocal() as session:
                stmt = select(JobDB).where(JobDB.id == job_id)
                result = await session.execute(stmt)
                job = result.scalar_one_or_none()
                
                if job:
                    await session.delete(job)
                    await session.commit()
                    logger.info(f"Deleted job {job_id}")
                    return True
                else:
                    logger.warning(f"Job {job_id} not found for deletion")
                    return False
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False
    
    @staticmethod
    async def cleanup_old_jobs(days: int = 30) -> int:
        """Clean up jobs older than specified days."""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            async with AsyncSessionLocal() as session:
                stmt = select(JobDB).where(JobDB.created_at < cutoff_date)
                result = await session.execute(stmt)
                old_jobs = result.scalars().all()
                
                for job in old_jobs:
                    await session.delete(job)
                
                await session.commit()
                deleted_count = len(old_jobs)
                logger.info(f"Cleaned up {deleted_count} old jobs")
                return deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup old jobs: {e}")
            return 0 