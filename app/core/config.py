from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


class Settings(BaseSettings):
    BASE_URL: str
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
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

settings = Settings(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
)
