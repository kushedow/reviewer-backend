import os
from fastapi.middleware.cors import CORSMiddleware

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

}

ALLOWED_FILETYPES = (".js", ".java", ".py", ".class", ".gitignore")


origins = [
    "https://student-care.sky.pro",
    "http://localhost",
    "http://localhost:10000",
]


def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
