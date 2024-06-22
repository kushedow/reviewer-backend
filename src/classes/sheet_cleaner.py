import asyncio

from gspread import Client, Worksheet, Spreadsheet
from loguru import logger

class SheetCleaner:

    def __init__(self, g_client, sheet_ids):
        self.__google_client: Client = g_client
        self.__sheet_ids: dict[str, str] = sheet_ids

    async def clean_sheet(self, sheet_name: str, range_str: str, worksheet_name: str | None = None):
        try:
            sheet_id = self.__sheet_ids[sheet_name]
            sheet: Spreadsheet = await asyncio.to_thread(self.__google_client.open_by_key, sheet_id)
            if worksheet_name:
                worksheet: Worksheet = await asyncio.to_thread(sheet.worksheet, worksheet_name)
            else:
                worksheet: Worksheet = await asyncio.to_thread(sheet.get_worksheet, 0)
            await asyncio.to_thread(worksheet.batch_clear, [range_str])
            logger.debug(f'Тестовые данные удалены из таблицы "{sheet_name}"')
        except Exception as e:
            logger.error(f'Ошибка при попытке очистки тестовых записей в таблице "{sheet_name}": {e}')
