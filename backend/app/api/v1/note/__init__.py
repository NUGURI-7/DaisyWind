"""
    @project: DaisyWind
    @Author: niu
    @file: __init__.py.py
    @date: 2026/3/8 21:14
    @desc:
"""
from fastapi import APIRouter

from backend.app.api.v1.note.note import router

note_router = APIRouter()


note_router.include_router(router, tags=['笔记'])
