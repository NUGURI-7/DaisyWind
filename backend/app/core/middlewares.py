import traceback

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class ResponseMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        method = request.method
        ip = request.client.host if request.client else "unknown"

        print(f"[请求] {method} {path} [ip地址] {ip}")

        try:
            response = await call_next(request)
        except Exception as exc:
            traceback.print_exc()
            response = JSONResponse(
                status_code=500,
                content={"code": 500, "message": "Internal Server Error", "data": None},
            )

        return response


def register_middlewares(app: FastAPI):
    app.add_middleware(ResponseMiddleware) # type: ignore
    app.add_middleware(
        CORSMiddleware, # type: ignore
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

