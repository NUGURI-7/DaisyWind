"""
    @project: Windify
    @Author: niu
    @file: __init__.py.py
    @date: 2026/2/3 20:49
    @desc:
"""
from fastapi import APIRouter

from backend.app.api.v1.user.user import router

user_router = APIRouter()
user_router.include_router(router, tags=['用户'])
