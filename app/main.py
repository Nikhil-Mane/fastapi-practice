from fastapi import FastAPI
from app.routes import v1, v2
from app.middleware.request_size import LimitRequestSizeMiddleware
from app.middleware.concurrent import limit_concurrent_requests
from app.core.config import settings
from app.core.limiter import limiter
from loguru import logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Custom API Gateway Application"
)

# Initialize rate limiter
app.state.limiter = limiter

# Middlewares
app.add_middleware(LimitRequestSizeMiddleware, max_body_size=settings.MAX_REQUEST_SIZE)
app.middleware("http")(limit_concurrent_requests)

# Routes
app.include_router(v1.router, prefix="/v1")
app.include_router(v2.router, prefix="/v2")

logger.info("Application startup complete") 