from gspread import Spreadsheet, Client
from gspread.worksheet import Worksheet
from loguru import logger

from src.models.ChecklistReport import ChecklistReport

class CriteriaPusher:

    def __init__(self, g_client, sheet_id):
        self.__google_client: Client = g_client
        self.__sheet_id: str = sheet_id
        self.__worksheet_index: int = 0
        self.__keys_to_push = {
            "ticket_id",
            "title",
            "grade",
            "student_full_name",
            "mentor_full_name",
            "stream_name",
        }

    def push_from_report(self, report: ChecklistReport):

        # собираем объект, чтобы добавить в табличку с отчетом

        rows_to_push: list = []

        for criteria in report.checklist_data.values():
            data_to_push = {
                "ticket_id": report.ticket_id,
                "title": criteria.get("title"),
                "grade": criteria.get("grade"),
                "student_full_name": report.student_full_name,
                "mentor_full_name": report.mentor_full_name,
                "stream_name": report.stream_name,
                "task_name": report.task_name,
                "skill": criteria.get("skill"),
            }

            logger.debug("Adding criteria report", value=data_to_push)
            rows_to_push.append(list(data_to_push.values()))

        sheet: Spreadsheet = self.__google_client.open_by_key(self.__sheet_id)
        worksheet: Worksheet = sheet.get_worksheet_by_id(self.__worksheet_index)
        worksheet.append_rows(rows_to_push)
