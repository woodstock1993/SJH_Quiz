from fastapi import FastAPI
from app.api.v1.router import api_router
from app.db.base import Base
from app.db.session import engine

app = FastAPI(
    title="SJH API",
    description="Project",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")