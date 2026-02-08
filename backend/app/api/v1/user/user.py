"""
    @project: Windify
    @Author: niu
    @file: user.py
    @date: 2026/2/3 20:49
    @desc:
"""
from fastapi import APIRouter, Depends

from backend.app.schemas.user_schema import UserLogin
from backend.app.services.user_service import UserService

router = APIRouter()

@router.post("/login", summary="用户登陆")
async def login(
        login_data: UserLogin,
        user_service: UserService = Depends(get_user_service)
):
    pass