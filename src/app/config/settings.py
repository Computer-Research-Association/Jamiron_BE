# infra/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_host: str
    redis_port: int
    session_ttl: int = 7 * 24 * 3600
    session_prefix: str = "sess"

    class Config:
        env_file = ".env"

settings = Settings()