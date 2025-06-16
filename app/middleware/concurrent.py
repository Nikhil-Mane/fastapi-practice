import asyncio
from fastapi import Request
from app.core.config import settings

semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_REQUESTS)

async def limit_concurrent_requests(request: Request, call_next):
    async with semaphore:
        response = await call_next(request)
        return response 