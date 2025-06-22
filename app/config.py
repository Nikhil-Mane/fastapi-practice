# Configuration variables for the AsyncJobQueue project

import os
from typing import Optional

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "asyncjobqueue")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# Construct database URL
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# External API configuration
EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "https://dummyapi.io/endpoint")

# Logging configuration
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/job_status.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Application configuration
APP_NAME = "AsyncJobQueue API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A FastAPI-based asynchronous job queue system"

# Worker configuration
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "1"))
JOB_TIMEOUT = int(os.getenv("JOB_TIMEOUT", "300"))  # 5 minutes
CLEANUP_DAYS = int(os.getenv("CLEANUP_DAYS", "30"))  # Clean up jobs older than 30 days 