import os
from json import JSONDecodeError
import gspread
from loguru import logger

from fastapi import FastAPI, Request
from gspread import SpreadsheetNotFound
from openai import AsyncOpenAI
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from classes.SkillProcessor import SkillProcessor
from classes.SkillPusher import SkillPusher
from classes.SkillRecord import SkillRecord
from exceptions.SkillApiError import SkillApiError

app = FastAPI()

# настраиваем корс
origins = ["https://student-care.sky.pro", "http://localhost", "http://localhost:10000",]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

CREDENTIALS_PATH = os.environ.get("CREDENTIALS_PATH")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SKILLS_REPORTS_DOCUMENT = "1hX_6SQTRp3iprm400GzAq6ImX_8EwtygYfKudnqI2OA"

if OPENAI_API_KEY is None:
    raise NameError("OPENAI_API_KEY is not set")

#  клиент для работы с таблицами
gc = gspread.service_account(filename=CREDENTIALS_PATH)
#  объект для отправки отчета по достижению скиллов в таблицы
pusher = SkillPusher(gc, SKILLS_REPORTS_DOCUMENT)
#  объект для превращения сырого чеклиста в отчет по достижению скиллов
skill_processor = SkillProcessor()
# объект для доступа в нейронке
client = AsyncOpenAI( api_key=OPENAI_API_KEY)


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


@app.post("/generate")
async def generate(request: Request):
    try:
        data = await request.json()
    except JSONDecodeError:
        return JSONResponse({"error": "incorrect JSON, try again"}, status_code=400)

    if "q" not in data:
        return JSONResponse({"error": "incorrect query, key q expected"}, status_code=400)

    prompt = data["q"]
    completion = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    response = completion.choices[0].message.content
    return {"response": response}


@app.post("/report")
async def save_report(request: Request):

    try:
        data = await request.json()
    except JSONDecodeError:
        return JSONResponse({"error": "incorrect JSON, try again"}, status_code=400)

    try:
        ticket_id = int(data["ticket_id"])
    except KeyError:
        return JSONResponse({"error": "incorrect query, key ticket_id expected"}, status_code=400)

    try:
        checklist_data = data["checklist_data"]
    except KeyError:
        return JSONResponse({"error": "incorrect query, key checklist_data expected"}, status_code=400)

    skill_records_to_push: list[SkillRecord] = skill_processor.build_skill_records(checklist_data, ticket_id)

    try:
        result = pusher.push(skill_records_to_push)
    except (SkillApiError, ValueError) as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    logger.debug(result)
    return [skill.model_dump() for skill in skill_records_to_push]
