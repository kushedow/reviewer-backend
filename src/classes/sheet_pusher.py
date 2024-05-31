import datetime

from gspread import Client, Worksheet, Spreadsheet
from gspread.worksheet import JSONResponse
from loguru import logger
from pydantic import BaseModel

from src.models.ai_request import AIRequest
from src.models.checklist_report import ChecklistReport
from src.models.softskills_report import SoftskillsReport


class SheetPusher:

    def __init__(self, g_client, sheet_ids):
        self.__google_client: Client = g_client
        self.__sheet_ids: dict[str, str] = sheet_ids

    def push_criteria_from_report(self, report: ChecklistReport):

        # собираем объект, чтобы добавить в табличку с отчетом

        rows_to_push: list = []

        for criteria in report.checklist_data.values():
            data_to_push = {
                "ticket_id": report.ticket_id,
                "student_id": report.student_id,
                "title": criteria.get("title"),
                "grade": criteria.get("grade"),
                "student_full_name": report.student_full_name,
                "mentor_full_name": report.mentor_full_name,
                "stream_name": report.stream_name,
                "task_name": report.task_name,
                "step": criteria.get("step"),
                "skill": criteria.get("skill"),
                "note": criteria.get("note")
            }

            logger.debug("Adding criteria report", value=data_to_push)
            rows_to_push.append(list(data_to_push.values()))

        sheet_id = self.__sheet_ids["CRITERIA"]
        sheet: Spreadsheet = self.__google_client.open_by_key(sheet_id)
        worksheet: Worksheet = sheet.worksheet("criteria")
        result = worksheet.append_rows(rows_to_push)
        return result

    def push_ai_generation_from_request(self, model: AIRequest, output_text):

        sheet_id = self.__sheet_ids["GENERATIONS"]
        document: Spreadsheet = self.__google_client.open_by_key(sheet_id)
        sheet: Worksheet = document.get_worksheet(0)

        created_at = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        result: JSONResponse = sheet.append_row([
            created_at,
            model.ticket_id,
            model.mentor_full_name,
            model.feedback_body,
            output_text
        ])

        return result

    def push_activity_from_request(self, model: BaseModel, event=""):

        sheet_id = self.__sheet_ids["ACTIVITIES"]
        document: Spreadsheet = self.__google_client.open_by_key(sheet_id)
        sheet: Worksheet = document.get_worksheet(0)
        current_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        result: JSONResponse = sheet.append_row([
            current_time,
            model.ticket_id,
            model.mentor_full_name,
            event
        ])

        return result

    def push_softskills_from_request(self, report: SoftskillsReport):

        sheet_id = self.__sheet_ids["SOFTSKILLS"]

        document: Spreadsheet = self.__google_client.open_by_key(sheet_id)
        worksheet: Worksheet = document.get_worksheet(0)
        current_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        rows_to_push = []

        for one_skill, one_value in report.skills.items():
            data = {
                "ticket_id": report.ticket_id,
                "student_id": report.student_id,
                "student_full_name": report.student_full_name,
                "mentor_full_name": report.mentor_full_name,
                "task_name": report.task_name,
                "key": one_skill,
                "value": one_value,
                "created_at": current_time,
            }
            rows_to_push.append(list(data.values()))
        logger.debug(f"Записываем {len(rows_to_push)} записей в табличку со скиллами")
        result = worksheet.append_rows(rows_to_push)
        return result

    def push_save_request_to_wiki(self, student_id: str, skill: str):
        """ Save student request to WIKI_REQUESTS google sheet """

        sheet_id = self.__sheet_ids["WIKI_REQUESTS"]
        document: Spreadsheet = self.__google_client.open_by_key(sheet_id)
        sheet: Worksheet = document.get_worksheet(0)
        current_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        result: JSONResponse = sheet.append_row([
            current_time,
            student_id,
            skill
        ])
        logger.debug(f'Записываем {result} в табличку "Все обращения к ВИКИ"')

        return result
