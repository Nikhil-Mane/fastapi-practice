import asyncio
import logging
import subprocess
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.db import init_db, close_db
from app.services.worker import start_workers, stop_workers
from app.routes.jobs import router as jobs_router

logger = logging.getLogger(__name__)

async def setup_database():
    """Automatically setup database connection."""
    try:
        # Try to initialize database (will fail if DB doesn't exist)
        await init_db()
        logger.info("✅ Connected to existing database")
        return True
    except Exception as e:
        logger.warning(f"Database connection failed: {e}")
        logger.info("🔄 Attempting to create database...")
        
        try:
            # Check if Docker is running
            result = subprocess.run(
                ["docker", "info"], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.error("❌ Docker is not running")
                logger.info("💡 Please start Docker Desktop or install PostgreSQL locally")
                logger.info("💡 For Docker: Start Docker Desktop application")
                logger.info("💡 For local PostgreSQL: Install and create database 'asyncjobqueue'")
                return False
            
            # Check if PostgreSQL container is already running
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=postgres-jobqueue", "--format", "{{.Names}}"],
                capture_output=True, text=True
            )
            
            if "postgres-jobqueue" not in result.stdout:
                logger.info("🚀 Starting PostgreSQL in Docker...")
                subprocess.run([
                    "docker", "run", "--name", "postgres-jobqueue",
                    "-e", "POSTGRES_DB=asyncjobqueue",
                    "-e", "POSTGRES_USER=postgres", 
                    "-e", "POSTGRES_PASSWORD=password",
                    "-p", "5432:5432",
                    "-d", "postgres:13"
                ], check=True)
                
                # Wait for database to be ready
                logger.info("⏳ Waiting for database to be ready...")
                time.sleep(10)
            
            # Try to initialize again
            await init_db()
            logger.info("✅ Database created and connected successfully")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Docker command timed out - Docker may not be running")
            logger.info("💡 Please start Docker Desktop")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to start PostgreSQL in Docker: {e}")
            logger.info("💡 Please ensure Docker is running or PostgreSQL is installed locally")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to setup database: {e}")
            return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle events."""
    try:
        # Setup database automatically
        db_ready = await setup_database()
        if not db_ready:
            logger.error("❌ Cannot start application without database")
            logger.info("🔧 Manual setup required:")
            logger.info("   1. Start Docker Desktop, OR")
            logger.info("   2. Install PostgreSQL and create database 'asyncjobqueue'")
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