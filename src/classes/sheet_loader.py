from gspread import Client, Worksheet, Spreadsheet
from loguru import logger


class SheetLoader:

    def __init__(self, g_client, sheet_ids):
        self.__google_client: Client = g_client
        self.__sheet_ids: dict[str, str] = sheet_ids

    def get_all_rows(self, sheet_name: str, worksheet_name: str | None = None):
        try:
            sheet_id = self.__sheet_ids[sheet_name]
            sheet: Spreadsheet = self.__google_client.open_by_key(sheet_id)
            if worksheet_name:
                worksheet: Worksheet = sheet.worksheet(worksheet_name)
            else:
                worksheet: Worksheet = sheet.get_worksheet(0)
            all_values = worksheet.get_all_values()
            return all_values
        except Exception as e:
            logger.error(f'Ошибка при попытке получить данные из таблицы "{sheet_name}": {e}')
