from time import sleep

from fastapi import APIRouter, Request

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