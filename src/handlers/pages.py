from fastapi import APIRouter, Request, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.config import METRICA_CODE

import markdown2

from loguru import logger

from src.dependencies import wiki_loader, sheet_pusher, wiki_ai_booster

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/explain/{slug}", tags=["Explain"])
async def explain(request: Request, slug: str, background_tasks: BackgroundTasks, student_id: str = None):
    logger.debug("Запущена загрузка статьи по скиллу")

    try:
        if student_id:
            background_tasks.add_task(sheet_pusher.push_save_request_to_wiki, student_id=student_id, skill=slug)
            return RedirectResponse(f"/explain/{slug}", status_code=301)

        article = wiki_loader.get(slug)

        context = {
            "title": article.title,
            "article_text": article.html,
            "student_id": student_id,
            "slug": slug,
            "METRICA_CODE": METRICA_CODE,
            "request": request,
            "personalized": "false",
        }

        return templates.TemplateResponse("wiki/article.html", context)

    except KeyError:
        return HTMLResponse(content="Не получилось найти такую статью", status_code=404)


# PROTOTYPE

@router.get("/explain/{slug}/personalize", tags=["Explain"])
async def explain(request: Request, slug: str, profession: str = Query(""), student_id: str = Query(""), ):
    logger.debug("Запущена загрузка статьи по скиллу c персонализацией")

    try:
        article = wiki_loader.get(slug)
        article_raw = article.article
        article_personalized = await wiki_ai_booster.improve(article_raw, profession)

        logger.debug(article_personalized)

        article_text = markdown2.markdown(article_personalized, extras=["code-friendly", "fenced-code-blocks"])

        context = {
            "title": article.title,
            "article_text": article_text,
            "student_id": student_id,
            "slug": slug,
            "METRICA_CODE": METRICA_CODE,
            "request": request,
            "personalized": "true",
        }

        return templates.TemplateResponse("wiki/personal-article.html", context)

    except KeyError:
        return HTMLResponse(content="Не получилось найти такую статью", status_code=404)

@router.get("/explain/{slug}/rate", tags=["Explain"])
async def rated(
        request: Request,
        background_tasks: BackgroundTasks,
        slug: str,
        student_id: int = Query(""),
        grade: int = Query(""),
        personalized: str = Query("")
):
    logger.debug(f"Поставлена оценка учеником {{ rate_request.student_id }} для статьи {{ rate_request.slug }} ")
    context = {"slug": slug, "student_id": student_id, "request": request}

    background_tasks.add_task(
        sheet_pusher.push_wiki_rate, slug=slug, grade=grade, student_id=student_id, personalized=personalized
    )

    return templates.TemplateResponse("wiki/rated.html", context)
