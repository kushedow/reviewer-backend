import os
import gspread

from fastapi import FastAPI
from gspread import SpreadsheetNotFound, GSpreadException
from openai import AsyncOpenAI, OpenAIError
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.classes.activity_pusher import ActivityPusher
from src.classes.ai_feedback_builder import AIFeedBackBuilder
from src.classes.ai_pusher import AIPusher
from src.classes.checklist_builder import ChecklistBuilder
from src.classes.criteria_pusher import CriteriaPusher
from src.classes.prompts_loader import PromptsLoader, PromptException
from src.models.AIRequest import AIRequest
from src.models.ChecklistReport import ChecklistReport
from src.models.ChecklistRequest import ChecklistRequest

# Достаем все конфиги
import src.config as config

app = FastAPI()

# настраиваем корс
origins = ["https://student-care.sky.pro", "http://localhost", "http://localhost:10000", ]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])

if config.OPENAI_API_KEY is None:
    raise NameError("OPENAI_API_KEY is not set")

#  клиент для работы с таблицами
gc = gspread.service_account(filename=config.CREDENTIALS_PATH)
#  объект для отправки отчета по достижению критериев
criteria_pusher = CriteriaPusher(gc, config.CRITERIA_REPORTS_DOCUMENT)
# объект для отправки отчета по открытию и закрытию проверки
activity_pusher = ActivityPusher(gc, config.ACTIVITIES_REPORTS_DOCUMENT)
# объект для отправки записей про AI генераций
ai_pusher = AIPusher(gc, config.GENERATIONS_REPORTS_DOCUMENT)
# объект для сборки критериев из таблиц
checklist_builder = ChecklistBuilder(gc, config.INDICES_DOCUMENT)
# объект для загрузки промптов
prompts_loader = PromptsLoader(gc, config.PROMPTS_DOCUMENT)
# объект для доступа в нейронке
ai_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
# объект для генерации фидбека нейроночкой
feedback_builder = AIFeedBackBuilder(ai_client, prompts_loader, ai_pusher)

@app.post("/checklist", tags=["Checklist"])
async def build_checklist(checklist_request: ChecklistRequest):
    """Если sheet_id на док задана - используем еу. Иначе используем название"""
    try:
        if checklist_request.sheet_id:
            checklist = checklist_builder.build(checklist_request.sheet_id)
        elif checklist_request.task_name:
            checklist = checklist_builder.build_by_task_name(checklist_request.task_name)
        else:
            return JSONResponse({"error": "task_name or sheet_id expected"}, status_code=400)

    except (GSpreadException, ValueError, SpreadsheetNotFound) as error:
        return JSONResponse({"error": str(error)}, status_code=400)

    try:
        # делаем запись об открытии тикета
        activity_pusher.push(model=checklist_request, event="open")

    except GSpreadException as error:
        return JSONResponse({"error": str(error)}, status_code=400)

    return JSONResponse(checklist, status_code=200)


@app.get("/refresh", tags=["Utils"])
async def refresh():
    """
    Сбрасывает кэш и заново перегружает критерии и промпты
    """
    checklist_builder.reload()
    prompts_loader.reload()
    return JSONResponse({"message": "Кэш промптов и чеклистов сброшен"}, status_code=200)


@app.post("/generate", tags=["AI"])
async def generate(ai_request: AIRequest):
    """
    Генерирует мотивирующую обратную связь для
    :param ai_request:
    :return:
    """

    try:
        completion = await ai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": ai_request.q}]
        )
        response = completion.choices[0].message.content

        # логируем
        ai_pusher.push(ai_request, response)
        return {"response": response}

    except OpenAIError as error:
        return JSONResponse({"error": error}, status_code=500)


@app.post("/generate-motivation", tags=["AI"])
async def generate_motivation(ai_request: AIRequest):
    """
   Генерирует мотивирующую обратную связь
   :param ai_request:
   """
    try:
        result = await feedback_builder.build(ai_request)
        return {"response": result}

    except PromptException as error:
        return JSONResponse({"error": "Ошибка при загрузке промпта, проверьте имя"}, status_code=400)

    except GSpreadException as error:
        return JSONResponse({"error": error}, status_code=400)

    except OpenAIError as error:
        return JSONResponse({"error": error}, status_code=400)


@app.post("/report", tags=["Report"])
async def save_report(report: ChecklistReport):
    try:
        # делаем запись о закрытии тикета
        activity_pusher.push(model=report, event="close")
        # делаем запись по критериям
        criteria_pusher.push_from_report(report=report)

    except GSpreadException as error:
        return JSONResponse({"error": error}, status_code=400)

    return JSONResponse({"message": "success"}, status_code=201)


@app.get("/prompts", tags=["AI"])
async def list_prompts():
    return prompts_loader.list()


@app.get("/prompts/{name}", tags=["AI"])
async def get_prompt_by_name(name: str):
    return prompts_loader.get(name)
