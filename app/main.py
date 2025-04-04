from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api.v1.router import router
from app.core.config import redis_client

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

@app.get("/cache")
def get_cache(key: str):
    value = redis_client.get(key)
    if value is None:
        return {"error": "Key not found"}
    return {"key": key, "value": value}

@app.post("/cache")
def set_cache(key: str, value: str):
    redis_client.set(key, value)
    return {"message": f"Key '{key}' has been set!"}

@app.put("/cache")
def update_cache(key: str, value: str):
    redis_client.set(key, value)
    return {"message": f"Key '{key}' has been updated"}

@app.delete("/cache")
def delete_cache(key: str):
    deleted_count = redis_client.delete(key)
    if deleted_count == 0:
        return {"error": "Key not found"}
    return {"message": f"Key '{key}' has been deleted"}

app.include_router(router, prefix="/api/v1")