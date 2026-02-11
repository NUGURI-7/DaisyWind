"""
    @project: DaisyWind
    @Author: niu
    @file: user_schema.py
    @date: 2026/2/3 21:20
    @desc:
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class UserLogin(BaseModel):
    """Login request body"""

    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserRegister(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    nick_name: str = Field(..., min_length=1, max_length=50, description="昵称")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserResponse(BaseModel):
    """用户信息响应"""
    uuid: UUID
    username: str
    nick_name: str
    rank_title: str
    email: str
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2，支持从 ORM 对象转换


class TokenResponse(BaseModel):
    """登录成功返回的 Token"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse