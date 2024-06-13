from fastapi import APIRouter, BackgroundTasks
from loguru import logger
from starlette.responses import JSONResponse

from gspread import GSpreadException
from openai import OpenAIError, PermissionDeniedError, RateLimitError, APIConnectionError
from src.classes.prompts_loader import PromptException

from src.dependencies import sheet_pusher, checklist_builder, prompts_loader, feedback_builder, skillset

from src.models.ai_request import AIRequest
from src.models.checklist import Checklist, ChecklistStatusEnum
from src.models.checklist_report import ChecklistReport
from src.models.checklist_request import ChecklistRequest
from src.models.softskills_report import SoftskillsReport

router = APIRouter()


@router.post("/checklist/full", tags=["Checklist Full"])
async def build_checklist_full(checklist_request: ChecklistRequest):
    logger.debug("Генерируем полный чеклист по его названию")
    checklist: Checklist = checklist_builder.get(checklist_request.task_name)

    if checklist.status == ChecklistStatusEnum.ERROR:
        return JSONResponse(
            {"error": "An error occurred on server while parsing the checklist"}, status_code=500
        )
    if not checklist.is_ready:
        return JSONResponse({"error": "Checklist is not ready"}, status_code=404)
    if checklist is None:
        return JSONResponse({"error": "Checklist not found"}, status_code=404)

    return checklist.model_dump()


@router.post("/checklist", tags=["Checklist"])
async def build_checklist(checklist_request: ChecklistRequest):
    """
    Возвращаем структурированный чеклист.
    Если sheet_id на док задана - используем его.
    Иначе используем название
    """

    if checklist_request.sheet_id:
        logger.debug("Генерируем чеклист по id документа")
        checklist = checklist_builder.find("sheet_id", checklist_request.sheet_id)
        if checklist is None:
            return JSONResponse({"error": "checklist not found"}, status_code=404)

    elif checklist_request.task_name:
        logger.debug("Генерируем чеклист по его названию")
        checklist = checklist_builder.get(checklist_request.task_name)
        if checklist is None:
            return JSONResponse({"error": "checklist not found"}, status_code=404)

    else:
        return JSONResponse({"error": "task_name or sheet_id expected"}, status_code=400)

    # делаем запись об открытии тикета

    try:
        sheet_pusher.push_activity_from_request(model=checklist_request, event="open")
    except GSpreadException as error:
        return JSONResponse({"error": str(error)}, status_code=500)

    if checklist.status.value == "OK":

        # досыпаем дополнительные поля
        skillset.enrich(checklist)

        return JSONResponse(checklist.body, status_code=200)
    else:
        return JSONResponse({"error": f"checklist found but status is {checklist.status.value}"}, status_code=500)


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
async def save_report(report: ChecklistReport, background_tasks: BackgroundTasks):
    try:

        # делаем запись о закрытии тикета
        background_tasks.add_task(sheet_pusher.push_activity_from_request, model=report, event="close")

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
        return JSONResponse({"error": str(error)}, status_code=400)

    return JSONResponse({"message": "success"}, status_code=201)


@router.get("/prompts", tags=["AI"])
async def list_prompts():
    return prompts_loader.list()


@router.get("/prompts/{name}", tags=["AI"])
async def get_prompt_by_name(name: str):
    try:
        prompt_content = prompts_loader.get(name)
        return prompt_content
    except PromptException as error:
        return JSONResponse({"error": str(error)}, status_code=404)
