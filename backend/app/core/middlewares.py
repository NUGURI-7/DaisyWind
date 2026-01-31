from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

class ResponseMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)


    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:

        path = request.url.path
        method = request.method
        ip = request.client.host

        print(f"[请求] {method} {path} [ip地址] {ip}")
        response = await call_next(request)

        return response


def register_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware, # type: ignore
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(ResponseMiddleware) # type: ignore