# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BASE_URL: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_URL: str

    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
