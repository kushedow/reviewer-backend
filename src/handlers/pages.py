from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="src/templates")

import markdown2

from loguru import logger

from src.dependencies import wiki_loader, sheet_pusher, wiki_ai_booster

router = APIRouter()


@router.get("/explain/{skill}", tags=["Explain"])
async def explain(request: Request, skill: str, student_id: str = None):
    logger.debug("Запущена загрузка статьи по скиллу")

    try:
        if student_id:
            sheet_pusher.push_save_request_to_wiki(student_id, skill)
            return RedirectResponse(url=f"/explain/{skill}", status_code=301)

        article = wiki_loader.load_wiki_by_skill(skill)
        article_text = markdown2.markdown(article, extras=["code-friendly", "fenced-code-blocks"])

        context = {"article_text": article_text}
        context.update({"request": request})

        return templates.TemplateResponse("wiki.html", context)

    except KeyError:
        return HTMLResponse(content="Не получилось найти такую статью", status_code=404)

# PROTOTYPE

@router.get("/explain/{skill}/personalize", tags=["Explain"])
async def explain(request: Request, skill: str, student_id: str = None):
    logger.debug("Запущена загрузка статьи по скиллу c персонализацией")

    article_raw = wiki_loader.load_wiki_by_skill(skill)
    article_personalized = await wiki_ai_booster.improve(article_raw)

    logger.debug(article_personalized)

    article_text = markdown2.markdown(article_personalized, extras=["code-friendly", "fenced-code-blocks"])

    context = {"article_text": article_text}
    context.update({"request": request})

    return templates.TemplateResponse("wiki.html", context)




