# infra/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_host: str
    redis_port: int
    session_ttl: int
    session_prefix: str

    class Config:
        env_file = ".env"

settings = Settings()