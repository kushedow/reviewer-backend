import asyncio

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.staticfiles import StaticFiles

from src.config import setup_cors
from src.dependencies import reload_cache

from src.handlers.api import router as api_router
from src.handlers.pages import router as auxiliary_api_router
from src.handlers.pages import router as pages_router

app = FastAPI()

setup_cors(app)

app.include_router(api_router)
app.include_router(auxiliary_api_router)
app.include_router(pages_router)

# Запускаем кеширование при старте приложения
asyncio.create_task(reload_cache())

class DisableCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        if request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-store"
        return response

# Mount static files with custom middleware
app.add_middleware(DisableCacheMiddleware)

app.mount("/static", StaticFiles(directory="static"), name="static")
