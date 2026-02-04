"""
    @project: Windify
    @Author: niu
    @file: __init__.py.py
    @date: 2026/2/1 14:59
    @desc:
"""
from fastapi import APIRouter

from backend.app.api.v1.user import user_router

v1_router = APIRouter()



v1_router.include_router(user_router, prefix="/user")