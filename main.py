import os
from json import JSONDecodeError
import gspread

from fastapi import FastAPI, Request
from gspread import SpreadsheetNotFound, GSpreadException
from openai import AsyncOpenAI, OpenAIError
from pydantic import ValidationError
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from classes.ActivityPusher import ActivityPusher
from classes.ChecklistBuilder import ChecklistBuilder
from classes.CriteriaPusher import CriteriaPusher
from models.AIRequest import AIRequest
from models.ChecklistReport import ChecklistReport
from models.ChecklistRequest import ChecklistRequest

app = FastAPI()

# настраиваем корс
origins = ["https://student-care.sky.pro", "http://localhost", "http://localhost:10000", ]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])

CREDENTIALS_PATH = os.environ.get("CREDENTIALS_PATH")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
CRITERIA_REPORTS_DOCUMENT = "1hX_6SQTRp3iprm400GzAq6ImX_8EwtygYfKudnqI2OA"
ACTIVITIES_REPORTS_DOCUMENT = "1SkCYQkrRdsApiaVDCeHJ-nf5ro9rRaFGmKuCciOyzNA"

if OPENAI_API_KEY is None:
    raise NameError("OPENAI_API_KEY is not set")

#  клиент для работы с таблицами
gc = gspread.service_account(filename=CREDENTIALS_PATH)
#  объект для отправки отчета по достижению критериев
criteria_pusher = CriteriaPusher(gc, CRITERIA_REPORTS_DOCUMENT)
# объект для отправки отчета по открытию и закрытию проверки
activity_pusher = ActivityPusher(gc, ACTIVITIES_REPORTS_DOCUMENT)
# объект для сборки критериев из таблиц
checklist_builder = ChecklistBuilder(gc)
# объект для доступа в нейронке
ai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


# DEPRECATED
@app.get("/checklist/{sheet_id}")
async def get(sheet_id):
    try:
        # достаем файл
        file = gc.open_by_key(sheet_id)

        # проходимся по первым 5 вкладкам, в надежде найти критерии хоть где то
        for i in range(5):

            sheet = file.get_worksheet(i)
            if sheet is None:
                break
            # TODO add sheet check
            data = sheet.get_all_records()
            if len(data) > 0 and "title" in data[0]:
                return data

        return JSONResponse({"error": "no good checklist in this document"}, status_code=400)

    except PermissionError:
        return JSONResponse({"error": "file is not public"}, status_code=403)

    except SpreadsheetNotFound:
        return JSONResponse({"error": "file not found"}, status_code=404)


@app.post("/checklist")
async def build_checklist(checklist_request: ChecklistRequest):

    try:
        # собираем чек-лист из документа
        checklist = checklist_builder.build(checklist_request.sheet_id)
    except (GSpreadException, ValueError, SpreadsheetNotFound) as error:
        return JSONResponse({"error": str(error)}, status_code=400)

    try:
        # делаем запись об открытии тикета
        activity_pusher.push(
            ticket_id=checklist_request.ticket_id,
            mentor=checklist_request.mentor_full_name,
            event="open"
        )

    except GSpreadException as error:
        return JSONResponse({"error": str(error)}, status_code=400)

    return JSONResponse(checklist, status_code=200)


@app.post("/generate")
async def generate(ai_request: AIRequest):

    try:
        completion = await ai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": ai_request.q}]
        )
        response = completion.choices[0].message.content
        return {"response": response}

    except OpenAIError as error:
        return JSONResponse({"error": error}, status_code=500)


@app.post("/report")
async def save_report(report: ChecklistReport):

    try:
        # делаем запись о закрытии тикета
        activity_pusher.push(
            ticket_id=report.ticket_id,
            mentor=report.mentor_full_name,
            event="close"
        )
        # делаем запись по критериям
        criteria_pusher.push_from_report(report=report)

    except GSpreadException as error:
        return JSONResponse({"error": error}, status_code=400)

    return JSONResponse({"message": "success"}, status_code=201)
