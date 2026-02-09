"""
    @project: DaisyWind
    @Author: niu
    @file: user.py
    @date: 2026/2/3 20:49
    @desc:
"""
from fastapi import APIRouter, Depends

from backend.app.core.depends import get_user_service, get_current_user
from backend.app.core.response import success
from backend.app.models import User
from backend.app.schemas.user_schema import UserLogin, TokenResponse, UserResponse, UserRegister
from backend.app.services.user_service import UserService

router = APIRouter()


@router.post("/login", summary="用户登陆")
async def login(
        login_data: UserLogin,
        user_service: UserService = Depends(get_user_service)
):
    result = await user_service.login(login_data)
    return success(data=TokenResponse(
        access_token = result["access_token"],
        user=UserResponse.model_validate(result["user"])
    ).model_dump())

@router.post("/register",summary="用户注册")
async def register(
        register_data: UserRegister,
        user_service = Depends(get_user_service)
):
    user = await user_service.register(register_data)

    return success(
        data=UserResponse.model_validate(user).model_dump(),
        message="注册成功"
    )

@router.get("/current_user", summary="获取当前用户信息")
async def get_current_user(
        current_user: User = Depends(get_current_user)
):
    return success(data=UserResponse.model_validate(current_user).model_dump())