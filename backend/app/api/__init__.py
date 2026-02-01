from fastapi import APIRouter

from backend.app.api.routes import play

api_router = APIRouter()


api_router.include_router(play.router)

