from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Custom API Gateway"
    VERSION: str = "1.0.0"
    SECRET_KEY: str = "super-secret-key"
    ALGORITHM: str = "HS256"
    API_KEY: str = "my-api-key"
    MAX_REQUEST_SIZE: int = 1024 * 1024  # 1MB
    MAX_CONCURRENT_REQUESTS: int = 5

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 