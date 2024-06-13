import os

from fastapi import APIRouter, BackgroundTasks
from loguru import logger
from starlette.responses import JSONResponse

from src.dependencies import reload_cache

router = APIRouter()


@router.get("/refresh", tags=["Utils"])
async def refresh(background_tasks: BackgroundTasks):
    """
    Сбрасывает кэш и заново перегружает критерии и промпты
    """
    logger.info("Начал сброс кэша")
    background_tasks.add_task(reload_cache)
    return JSONResponse({"message": "Запущен сброс кэша чеклистов, статей и промптов. Займет несколько минут"},
                        status_code=200)


@router.get("/version", tags=["Utility"])
async def get_backend_version():
    version = os.environ.get("FRONTEND_MIN_VERSION", "0.0")
    return {"frontend__min_version": version}
