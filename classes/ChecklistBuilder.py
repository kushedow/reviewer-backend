from gspread import Client
from loguru import logger


class ChecklistBuilder:

    def __init__(self, g_client):
        self.__google_client: Client = g_client

    def build(self, sheet_id):

        logger.debug(f"Building checklist of {sheet_id}")

        # достаем файл
        file = self.__google_client.open_by_key(sheet_id)

        # проходимся по первым 5 вкладкам, в надежде найти критерии хоть где то
        for i in range(5):

            sheet = file.get_worksheet(i)
            if sheet is None:
                break
            # TODO add sheet check
            data = sheet.get_all_records()
            if len(data) > 0 and "title" in data[0]:
                return data

        raise ValueError("No good checklist in this document")

