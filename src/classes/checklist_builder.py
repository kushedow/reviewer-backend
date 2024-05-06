from gspread import Client
from loguru import logger


class ChecklistBuilder:

    def __init__(self, g_client, index_sheet):
        self.__google_client: Client = g_client
        self.__index_sheet = index_sheet
        self.__map = self._load_indices(index_sheet)

    def _load_indices(self, index_sheet_id):

        file = self.__google_client.open_by_key(index_sheet_id)
        sheet = file.worksheet("index")
        records = sheet.get_all_records()
        lessons_to_sheets = {record["lesson"]: record["sheet_id"] for record in records}
        return lessons_to_sheets

    def build_by_task_name(self, task_name):

        task_name = task_name.strip()
        task_name = task_name.replace("&nbsp;", " ")
        task_name = task_name.replace("  ", " ")

        sheet_id = self.__map.get(task_name)

        if sheet_id is None:
            raise KeyError("No checklist for this lesson name")
        checklist = self.build(sheet_id)
        return checklist

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

    def reload(self):
        self.__map = self._load_indices(self.__index_sheet)
