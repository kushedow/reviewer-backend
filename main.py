import os
from json import JSONDecodeError
import gspread

from fastapi import FastAPI, Query, Body, Request
from gspread import SpreadsheetNotFound
from openai import AsyncOpenAI
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


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

CREDENTIALS_PATH = os.environ.get("CREDENTIALS_PATH")

# gc = gspread.service_account()
gc = gspread.service_account(filename=CREDENTIALS_PATH)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if OPENAI_API_KEY is None:
    raise NameError("OPENAI_API_KEY is not set")

client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=OPENAI_API_KEY,
)

# os.environ["REQUESTS_CA_BUNDLE"] = "cacert.pem"

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

    if "checklist_data" not in data:
        return JSONResponse({"error": "incorrect query, key checklist_data expected"}, status_code=400)

    if "sheet_id" not in data:
        return JSONResponse({"error": "incorrect query, key checklist_url expected"}, status_code=400)

    return {"response": {}}
