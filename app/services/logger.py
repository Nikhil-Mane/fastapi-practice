import aiofiles

async def log_status(message):
    async with aiofiles.open("logs/job_status.log", mode="a") as f:
        await f.write(message + "\n") 