import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.staticfiles import StaticFiles

from src.config import setup_cors, SERVER
from src.dependencies import reload_cache

from src.handlers.api import router as api_router
from src.handlers.auxiliary_api import router as auxiliary_api_router
from src.handlers.pages import router as pages_router

if SERVER is None:
    raise ValueError("App is not started. SERVER must be set")

if SERVER == 'prod':
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Запускаем кеширование при старте приложения
        asyncio.create_task(reload_cache())
        yield


    app = FastAPI(lifespan=lifespan)
else:
    app = FastAPI()

setup_cors(app)

app.include_router(api_router)
app.include_router(auxiliary_api_router)
app.include_router(pages_router)


class DisableCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        if request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-store"
        return response


# Mount static files with custom middleware
app.add_middleware(DisableCacheMiddleware)

app.mount("/static", StaticFiles(directory="static"), name="static")
