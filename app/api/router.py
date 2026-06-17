from fastapi import APIRouter

from app.api.routes import health, metadata, root

api_router = APIRouter()
api_router.include_router(root.router)
api_router.include_router(health.router)
api_router.include_router(metadata.router)
