import os
from json import JSONDecodeError
import gspread
from loguru import logger

from fastapi import FastAPI, Query, Body, Request
from gspread import SpreadsheetNotFound
from openai import AsyncOpenAI
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from utils import __grab_keys_from_sheet, __count_min_value_by_criteria, __count_avg_value_by_topic

origins = [
    "https://student-care.sky.pro",
    "http://localhost",
    "http://localhost:10000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOPICS_TAB = "topics"
CRITERIA_TAB = "criteria"
CREDENTIALS_PATH = os.environ.get("CREDENTIALS_PATH")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if OPENAI_API_KEY is None:
    raise NameError("OPENAI_API_KEY is not set")

# gc = gspread.service_account()
gc = gspread.service_account(filename=CREDENTIALS_PATH)

client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=OPENAI_API_KEY,
)


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


@app.post("/report/")
async def save_report(request: Request):
    try:
        data = await request.json()
    except JSONDecodeError:
        return JSONResponse({"error": "incorrect JSON, try again"}, status_code=400)

    try:
        ticket_id = data["ticket_id"]
    except KeyError:
        return JSONResponse({"error": "incorrect query, key ticket_id expected"}, status_code=400)

    try:
        checklist_data = data["checklist_data"].values()
    except KeyError:
        return JSONResponse({"error": "incorrect query, key checklist_data expected"}, status_code=400)

    try:
        sheet_id = data["sheet_id"]
    except KeyError:
        return JSONResponse({"error": "incorrect query, key sheet_id expected"}, status_code=400)

    try:

        if "http" in sheet_id:
            sheet_id = max(sheet_id.split("/"), key=len)
            logger.debug(f"Link received, opening {sheet_id}")

        file = gc.open_by_key(sheet_id)

    except PermissionError:
        return JSONResponse({"error": "file is not public"}, status_code=403)

    except SpreadsheetNotFound:
        return JSONResponse({"error": "file not found"}, status_code=404)

    # Добавление в cтатистику

    topics_sheet = file.worksheet(TOPICS_TAB)
    topics_row_to_push = [ticket_id]
    for result_key in __grab_keys_from_sheet(topics_sheet):
        average_percent = __count_avg_value_by_topic(checklist_data, result_key)
        topics_row_to_push.append(average_percent)

    topics_sheet.append_row(topics_row_to_push)

    # Добавление в критерии

    criteria_sheets = file.worksheet(CRITERIA_TAB)
    criteria_row_to_push = [ticket_id]
    for result_key in __grab_keys_from_sheet(criteria_sheets):
        min_grade = __count_min_value_by_criteria(checklist_data, result_key)
        criteria_row_to_push.append(min_grade)

    criteria_sheets.append_row(criteria_row_to_push)


    return {"topics": topics_row_to_push, "creiteria": criteria_row_to_push}
