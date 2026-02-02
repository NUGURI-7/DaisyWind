from time import sleep

from fastapi import APIRouter, Request

from backend.app.models import User

router = APIRouter(prefix="/play",tags=["PLAY"])


@router.get("/redis")
async def redis_set(request: Request):
    value =await request.app.state.redis.client.get("nuguri")


    if value is None:
        sleep(5)
        hi = 'hey, nuguri'
        await request.app.state.redis.client.set(
            'nuguri',
            hi,
            ex=60
        )
        return hi

    return value




@router.get("/test")
async def get_user(request: Request):
    user =  await User.filter(username='admin').first()

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    }
