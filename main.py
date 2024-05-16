from fastapi import FastAPI, Depends
from starlette.staticfiles import StaticFiles

from src.config import setup_cors
from src.handlers.api import router as api_router
from src.handlers.pages import router as pages_router

app = FastAPI()
setup_cors(app)

app.include_router(api_router)
app.include_router(pages_router)

app.mount("/static", StaticFiles(directory="static"), name="static")
