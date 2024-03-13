import datetime

from gspread import Spreadsheet, Client
from gspread.worksheet import JSONResponse, Worksheet
from loguru import logger


class ActivityPusher:

    def __init__(self, g_client, sheet_id):
        self.__google_client: Client = g_client
        self.__sheet_id: str = sheet_id

    def push(self, ticket_id=0, mentor="", event=""):

        document: Spreadsheet = self.__google_client.open_by_key(self.__sheet_id)
        sheet: Worksheet = document.get_worksheet(0)
        current_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        result: JSONResponse = sheet.append_row([current_time, ticket_id,  mentor, event])

        return result
