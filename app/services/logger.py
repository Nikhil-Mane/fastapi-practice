"""Logger utility for AsyncJobQueue."""
import aiofiles

async def log_status(message):
    """Log a status message to the job status log file."""
    async with aiofiles.open("logs/job_status.log", mode="a") as f:
        await f.write(message + "\n") 