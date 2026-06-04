from fastapi import APIRouter

from app.api.routes import health, plants, root

api_router = APIRouter()
api_router.include_router(root.router)
api_router.include_router(health.router)
api_router.include_router(plants.router)
