# infra/settings.py
from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    redis_host: str
    redis_port: int

    session_ttl: int
    session_prefix: str

    database_url: SecretStr
    # mysql_root_password: str
    # mysql_database: str
    # mysql_user: str
    # mysql_password: str

    class Config:
        env_file = ".env"

settings = Settings()