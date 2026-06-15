from fastapi import APIRouter

from app.api.routes import health, plants, reminders, root

api_router = APIRouter()
api_router.include_router(root.router)
api_router.include_router(health.router)
api_router.include_router(plants.router)
api_router.include_router(reminders.router)
