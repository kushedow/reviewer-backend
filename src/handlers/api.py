import os

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from gspread import SpreadsheetNotFound, GSpreadException
from openai import OpenAIError, PermissionDeniedError, RateLimitError, APIConnectionError
from src.classes.prompts_loader import PromptException

from src.dependencies import sheet_pusher, checklist_builder, prompts_loader, feedback_builder

from src.models.ai_request import AIRequest
from src.models.checklist_report import ChecklistReport
from src.models.checklist_request import ChecklistRequest
from src.models.softskills_report import SoftskillsReport

router = APIRouter()


@router.post("/checklist", tags=["Checklist"])
async def build_checklist(checklist_request: ChecklistRequest):
    """Возвращаем структурированный чеклист. Если sheet_id на док задана - используем его. Иначе используем название"""
    try:
        if checklist_request.sheet_id:
            checklist = checklist_builder.build(checklist_request.sheet_id)
        elif checklist_request.task_name:
            checklist = checklist_builder.build_by_task_name(checklist_request.task_name)
        else:
            return JSONResponse({"error": "task_name or sheet_id expected"}, status_code=400)

    # Если при загрузке произошла ошибка – вернем 400
    except (GSpreadException, SpreadsheetNotFound) as error:
        return JSONResponse({"error": str(error)}, status_code=400)

    # Если мы искали по имени и не нашли такого чеклиста – вернем 404
    except KeyError as error:
        return JSONResponse({"error": str(error)}, status_code=404)

    try:
        # делаем запись об открытии тикета
        sheet_pusher.push_activity_from_request(model=checklist_request, event="open")

    # Если не удалось записать отчет об открытии тикета – выкидываем 500
    except GSpreadException as error:
        return JSONResponse({"error": str(error)}, status_code=500)

    return JSONResponse(checklist, status_code=200)


@router.get("/refresh", tags=["Utils"])
async def refresh():
    """
    Сбрасывает кэш и заново перегружает критерии и промпты
    """
    checklist_builder.reload()
    prompts_loader.reload()
    return JSONResponse({"message": "Кэш промптов и чеклистов сброшен"}, status_code=200)


@router.post("/generate-motivation", tags=["AI"])
async def generate_motivation(ai_request: AIRequest):
    """
   Генерирует мотивирующую обратную связь
   :param ai_request:
   """
    try:
        result = await feedback_builder.build(ai_request)
        return {"response": result}

    except PromptException as error:
        return JSONResponse({"error": f"Ошибка при загрузке промпта, проверьте имя {str(error)}"}, status_code=400)

    except GSpreadException as error:
        return JSONResponse({"error": error}, status_code=400)

    except PermissionDeniedError as error:
        return JSONResponse({"error": "No access to OpenAI API"}, status_code=500)

    except RateLimitError as error:
        return JSONResponse({"error": "RateLimitError, check OpenAI account balance"}, status_code=500)

    except APIConnectionError as error:
        return JSONResponse({"error": "APIConnectionError, check OpenAI connection"}, status_code=500)

    except OpenAIError as error:
        return JSONResponse({"error": error}, status_code=400)


@router.post("/report", tags=["Report"])
async def save_report(report: ChecklistReport):
    """
    Сохраняем отчет как ученик сделал домашку
    :param report:
    :return:
    """
    try:
        # делаем запись о закрытии тикета
        sheet_pusher.push_activity_from_request(model=report, event="close")
        # делаем запись по критериям
        sheet_pusher.push_criteria_from_report(report=report)

    except GSpreadException as error:
        return JSONResponse({"error": error}, status_code=400)

    return JSONResponse({"message": "success"}, status_code=201)


@router.post("/report-soft-skills", tags=["Report"])
async def save_soft_skills_report(report: SoftskillsReport):
    """
    Сохраняем отчет по софтам
    :param report:
    :return:
    """
    try:
        sheet_pusher.push_softskills_from_request(report)

    except GSpreadException as error:
        return JSONResponse({"error": error}, status_code=400)

    return JSONResponse({"message": "success"}, status_code=201)


@router.get("/prompts", tags=["AI"])
async def list_prompts():
    return prompts_loader.list()


@router.get("/version", tags=["Utility"])
async def get_backend_version():
    version = os.environ.get("FRONTEND_MIN_VERSION", "0.0")
    return {"frontend__min_version": version}


@router.get("/prompts/{name}", tags=["AI"])
async def get_prompt_by_name(name: str):
    try:
        prompt_content = prompts_loader.get(name)
        return prompt_content
    except PromptException as error:
        return JSONResponse({"error": str(error)}, status_code=404)
