import os
from typing import List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings."""
    
    # Service Configuration
    SERVICE_NAME: str = "Task Generator Microservice"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8001, env="PORT")
    
    # Task Processor Configuration
    TASK_PROCESSOR_URL: str = Field(
        default="http://localhost:8000", 
        env="TASK_PROCESSOR_URL"
    )
    TASK_PROCESSOR_TIMEOUT: int = Field(default=30, env="TASK_PROCESSOR_TIMEOUT")
    
    # Task Generation Configuration
    GENERATION_INTERVAL: int = Field(default=5, env="GENERATION_INTERVAL")
    MAX_CONCURRENT_TASKS: int = Field(default=10, env="MAX_CONCURRENT_TASKS")
    BATCH_SIZE: int = Field(default=5, env="BATCH_SIZE")
    
    # Task Types and Weights
    TASK_TYPE_WEIGHTS: Dict[str, float] = {
        "http_request": 0.3,
        "math_calculation": 0.25,
        "file_operation": 0.25,
        "data_transformation": 0.2
    }
    
    # Priority Distribution
    PRIORITY_WEIGHTS: Dict[str, float] = {
        "high": 0.2,
        "normal": 0.6,
        "low": 0.2
    }
    
    # HTTP Request Configuration
    HTTP_ENDPOINTS: List[str] = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/users/1",
        "https://httpbin.org/get",
        "https://api.github.com/users/octocat",
        "https://api.publicapis.org/entries",
        "https://dog.ceo/api/breeds/image/random"
    ]
    
    # Database Configuration (for task history)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/taskgenerator",
        env="DATABASE_URL"
    )
    
    # Redis Configuration (for rate limiting and caching)
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Monitoring Configuration
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=8002, env="METRICS_PORT")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # Retry Configuration
    MAX_RETRIES: int = Field(default=3, env="MAX_RETRIES")
    RETRY_DELAY: int = Field(default=1, env="RETRY_DELAY")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings() 