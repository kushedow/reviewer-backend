import os
from fastapi.middleware.cors import CORSMiddleware

import asyncio
import gspread_asyncio
# from google-auth package
from google.oauth2.service_account import Credentials

CREDENTIALS_PATH = os.environ.get("CREDENTIALS_PATH")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

SHEET_IDS = {

    "CRITERIA": "1hX_6SQTRp3iprm400GzAq6ImX_8EwtygYfKudnqI2OA",
    "ACTIVITIES": "1SkCYQkrRdsApiaVDCeHJ-nf5ro9rRaFGmKuCciOyzNA",
    "GENERATIONS": "119WqXPSYDkALioEvvWZ_gqoaNIqQlk2X093m9sxPJtM",
    "INDICES": "1iS2zGIcv_e9EkhWB5jH5CVWHzb81h862XgHC-ZF_fCs",
    "PROMPTS": "1Mo0D4-oVvk0ukRDfnYyR09luzyrZ5iNGQmuX1sAzq3A",
    "SOFTSKILLS": "1O__0V3VvT6eFU_e7fRpfa5Bpc_v3dRXT3q15fU9sN9E",
    "WIKI": "1nZq1glJDQpoOCvu1WQWPBII9ifzgBzN1yhOnUCWfzbY",
    "WIKI_REQUESTS": "1mw0cIZz0HtLr_NKgU5Yx0UtPS5PaIxt0Rve9qqObv_A",
    "WIKI_RATES": "1Kh4rWSjGzBLHFGP__cLJHM-d39xfm4thiVwSy2DDDfc",

}

ALLOWED_FILETYPES = (".js", ".java", ".py", ".class", ".gitignore")


origins = [
    "https://student-care.sky.pro",
    "http://localhost",
    "http://localhost:10000",
]

METRICA_CODE = """       
       (function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
       m[i].l=1*new Date();
       for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
       k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})
       (window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");

       ym(97492095, "init", {
            clickmap:true,
            trackLinks:true,
            accurateTrackBounce:true,
            webvisor:true
       });
"""

def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def get_creds():
    # To obtain a service account JSON file, follow these steps:
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH)
    scoped = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return scoped
