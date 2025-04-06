from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api.v1.router import router
from app.utils.utils import redis_client

app = FastAPI(
    title="SJH_Quiz",
    description="Project",
    version="1.0.0"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="SJH API",
        version="1.0.0",
        description="JWT Token을 사용한 인증 방식",
        routes=app.routes,
    )
    
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})[""] = {
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(router, prefix="/api/v1")