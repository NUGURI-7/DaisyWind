"""
    @project: Windify
    @Author: niu
    @file: user_service.py.py
    @date: 2026/2/8 17:39
    @desc:
"""
from typing import Optional

from backend.app.models import User


class UserService:


    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        验证用户身份
        :param username:
        :param password:
        :return:
        """
        user = await User.filter(username=username).first()

        if not user:
            return None
        if not user.check_password(password):
            return None

        return user