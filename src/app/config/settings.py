# infra/settings.py
from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    model_config = {"extra": "ignore",
                    "env_file": ".env" }
    redis_host: str
    redis_port: int

    session_ttl: int
    session_prefix: str

    database_url: SecretStr


settings = Settings()