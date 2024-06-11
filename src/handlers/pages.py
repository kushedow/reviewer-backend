from fastapi import APIRouter, Request, Form, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.config import METRICA_CODE

import markdown2

from loguru import logger

from src.dependencies import wiki_loader, sheet_pusher, wiki_ai_booster

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/explain/{slug}", tags=["Explain"])
async def explain(request: Request, slug: str, student_id: str = None):
    logger.debug("Запущена загрузка статьи по скиллу")

    try:

        article = wiki_loader.get(slug)

        context = {
            "title": article.title,
            "article_text": article.html,
            "student_id": student_id,
            "slug": slug,
            "METRICA_CODE": METRICA_CODE,
            "request": request
        }

        return templates.TemplateResponse("wiki/article.html", context)

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

    context = {"article_text": article_text, "skill": skill, "METRICA_CODE": METRICA_CODE}

    context.update({"request": request})

    return templates.TemplateResponse("wiki/article.html", context)


@router.get("/explain/{slug}/rate", tags=["Explain"])
async def rated(
        request: Request,
        background_tasks: BackgroundTasks,
        slug: str,
        grade: int = Query(""),
        student_id: str = Query(""),
        personalized: str = Query("")
):

    logger.debug(f"Поставлена оценка учеником {{ rate_request.student_id }} для статьи {{ rate_request.slug }} ")
    context = {"slug": slug, "student_id": student_id, "request": request}

    background_tasks.add_task(sheet_pusher.push_wiki_rate, slug, student_id, grade, personalized)

    return templates.TemplateResponse("wiki/rated.html", context)
