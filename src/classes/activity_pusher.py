import datetime

from gspread import Spreadsheet, Client
from gspread.worksheet import JSONResponse, Worksheet
from loguru import logger
from pydantic import BaseModel


class ActivityPusher:

    def __init__(self, g_client, sheet_id):
        self.__google_client: Client = g_client
        self.__sheet_id: str = sheet_id

    def push(self, model: BaseModel,  event=""):

        document: Spreadsheet = self.__google_client.open_by_key(self.__sheet_id)
        sheet: Worksheet = document.get_worksheet(0)
        current_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        result: JSONResponse = sheet.append_row([
            current_time,
            model.ticket_id,
            model.mentor_full_name,
            event
        ])

        return result


