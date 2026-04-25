from fastapi import APIRouter

from app.routers import analytics, hooks, calendar

api_router = APIRouter()

api_router.include_router(analytics.router)
api_router.include_router(hooks.router)
api_router.include_router(calendar.router)
