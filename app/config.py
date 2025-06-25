"""Configuration variables for the AsyncJobQueue project."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings."""
    
    # Database configuration - prefer DATABASE_URL, fallback to individual variables
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    DB_HOST: str = Field(default="localhost", env="DB_HOST")
    DB_PORT: str = Field(default="5432", env="DB_PORT")
    DB_NAME: str = Field(default="asyncjobqueue", env="DB_NAME")
    DB_USER: str = Field(default="postgres", env="DB_USER")
    DB_PASSWORD: str = Field(default="password", env="DB_PASSWORD")
    
    # Construct database URL
    @property
    def DB_URL(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # External API configuration
    EXTERNAL_API_URL: str = Field(default="https://dummyapi.io/endpoint", env="EXTERNAL_API_URL")
    
    # Logging configuration
    LOG_FILE_PATH: str = Field(default="logs/job_status.log", env="LOG_FILE_PATH")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Application configuration
    APP_NAME: str = "AsyncJobQueue API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "A FastAPI-based asynchronous job queue system"
    
    # Worker configuration
    MAX_WORKERS: int = Field(default=1, env="MAX_WORKERS")
    JOB_TIMEOUT: int = Field(default=300, env="JOB_TIMEOUT")  # 5 minutes
    CLEANUP_DAYS: int = Field(default=30, env="CLEANUP_DAYS")  # Clean up jobs older than 30 days
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Backward compatibility
DB_URL = settings.DB_URL 