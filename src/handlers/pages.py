from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="src/templates")

import markdown2

from loguru import logger
from starlette.responses import HTMLResponse

from src.dependencies import wiki_loader

router = APIRouter()


@router.get("/explain/{skill}", tags=["Explain"])
async def refresh(request: Request, skill: str):

    logger.debug("Запущена загрузка статьи по скиллу")

    try:
        article = wiki_loader.load_wiki_by_skill(skill)
        article_text = markdown2.markdown(article, extras=["code-friendly", "fenced-code-blocks"])

        context = {"article_text": article_text}
        context.update({"request": request})

        return templates.TemplateResponse("wiki.html", context)

    except KeyError:
        return HTMLResponse(content="Не получилось найти такую статью", status_code=404)
