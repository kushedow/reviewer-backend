import datetime

from gspread import Spreadsheet, Client
from gspread.worksheet import JSONResponse, Worksheet
from loguru import logger
from pydantic import BaseModel


class AIPusher:

    def __init__(self, g_client, sheet_id):
        self.__google_client: Client = g_client
        self.__sheet_id: str = sheet_id

    def push(self, model: BaseModel, output_text):

        document: Spreadsheet = self.__google_client.open_by_key(self.__sheet_id)
        sheet: Worksheet = document.get_worksheet(0)

        created_at = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        result: JSONResponse = sheet.append_row([
            created_at,
            model.ticket_id,
            model.mentor_full_name,
            model.q,
            output_text
        ])

        return result

