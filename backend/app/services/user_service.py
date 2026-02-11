"""
    @project: DaisyWind
    @Author: niu
    @file: user_service.py.py
    @date: 2026/2/8 17:39
    @desc:
"""
from typing import Optional

from backend.app.core.exceptions import AppAuthenticationFailed, ValidationException
from backend.app.core.security import create_access_token
from backend.app.models import User
from backend.app.schemas.user_schema import UserLogin, UserRegister


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

    async def login(self, login_data: UserLogin) -> dict:
        """
        User login
        :param login_data:
        :return:
        """
        user = await self.authenticate(login_data.username, login_data.password)

        if not user:
            raise AppAuthenticationFailed(message="Username or password error")

        access_token = create_access_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "user": user
        }

    async def register(self, register_data: UserRegister) -> User:
        """
        User register
        :param register_data:
        :return:
        """
        if await User.filter(username=register_data.username).exists():
            raise ValidationException(message="Username existed")

        if await User.filter(email=register_data.email).exists():
            raise ValidationException(message="Email existed")

        user = User(
            username=register_data.username,
            nick_name=register_data.nick_name,
            email=register_data.email
        )
        user.set_password(register_data.password)
        await user.save()

        return user



    async def get_user_by_id(self, user_id: str) -> Optional[User]:

        return await User.filter(id=user_id).first()