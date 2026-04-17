"""
    @project: DaisyWind
    @Author: niu
    @file: __init__.py.py
    @date: 2026/2/1 14:59
    @desc:
"""
from fastapi import APIRouter

from backend.app.api.v1.note import note_router
from backend.app.api.v1.user import user_router
from backend.app.api.v1.media.media import router as media_router
from backend.app.api.v1.chat import chat_router

v1_router = APIRouter()


v1_router.include_router(user_router, prefix="/user")
v1_router.include_router(note_router, prefix="/note")
v1_router.include_router(chat_router, prefix="/chat")
v1_router.include_router(media_router, prefix="/media", tags=["媒体资源"])