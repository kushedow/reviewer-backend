from gspread import Spreadsheet, Client
from gspread.worksheet import Worksheet
from loguru import logger


class PromptsLoader:

    def __init__(self, g_client, sheet_id):
        self.__google_client: Client = g_client
        self.__sheet_id: str = sheet_id
        self.__worksheet = None

        self.reload()

    def reload(self) -> None:
        file = self.__google_client.open_by_key(self.__sheet_id)
        self.__worksheet = file.get_worksheet(0)

    def list(self) -> list[str]:
        first_column_values = self.__worksheet.col_values(1)
        return first_column_values[1:]

    def get(self, name: str) -> str:
        cell = self.__worksheet.find(name, in_column=1)
        prompt_value = self.__worksheet.row_values(cell.row)[1]
        return prompt_value
