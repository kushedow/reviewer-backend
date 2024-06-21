import datetime
from typing import Any, MutableMapping

from gspread import Client, Worksheet, Spreadsheet
from loguru import logger

from src.models.ai_request import AIRequest
from src.models.checklist_report import ChecklistReport
from src.models.checklist_request import ChecklistRequest
from src.models.softskills_report import SoftskillsReport


class SheetPusher:

    def __init__(self, g_client, sheet_ids):
        self.__google_client: Client = g_client
        self.__sheet_ids: dict[str, str] = sheet_ids

    def __get_worksheet(self, sheet_name: str, worksheet_name: str | None = None) -> Worksheet:
        sheet_id = self.__sheet_ids[sheet_name]
        sheet: Spreadsheet = self.__google_client.open_by_key(sheet_id)
        if worksheet_name:
            return sheet.worksheet(worksheet_name)
        else:
            return sheet.get_worksheet(0)

    @staticmethod
    def __get_current_time() -> str:
        return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    def push_criteria_from_report(self, report: ChecklistReport) -> MutableMapping[str, Any]:
        """ Push checklist reports to CRITERIA google sheet """
        rows_to_push: list = []

        for criteria in report.checklist_data.values():
            data_to_push = {
                "id": report.ticket_id,
                "student_id": report.student_id,
                "criteria_name": criteria.get("title"),
                "grade": criteria.get("grade"),
                "mentor_full_name": report.mentor_full_name,
                "stream_name": report.stream_name,
                "lesson": report.task_name,
                "step": criteria.get("step"),
                "skill": criteria.get("skill"),
                "note": criteria.get("note"),
                "created_at": self.__get_current_time(),
            }
            logger.debug("Добавляем запись в табличку критериев", value=data_to_push)
            rows_to_push.append(list(data_to_push.values()))

        worksheet = self.__get_worksheet(sheet_name="CRITERIA", worksheet_name="criteria")
        result = worksheet.append_rows(rows_to_push)
        return result

    def push_ai_generation_from_request(self, model: AIRequest, output_text) -> MutableMapping[str, Any]:
        """ Push AI generation report to GENERATIONS google sheet """
        worksheet = self.__get_worksheet(sheet_name="GENERATIONS")
        created_at = self.__get_current_time()
        result = worksheet.append_row([
            created_at,
            model.ticket_id,
            model.mentor_full_name,
            model.feedback_body,
            output_text
        ])
        logger.debug(f"Записываем генерацию ИИ в табличку генерации")
        return result

    def push_activity_from_request(
            self, model: ChecklistReport | ChecklistRequest, event=""
    ) -> MutableMapping[str, Any]:
        """ Push activity report to ACTIVITIES google sheet """
        worksheet = self.__get_worksheet(sheet_name="ACTIVITIES")
        current_time = self.__get_current_time()
        result = worksheet.append_row([
            current_time,
            model.ticket_id,
            model.task_name,
            model.mentor_full_name,
            event
        ])
        logger.debug(f"Записываем эвент '{event}' в табличку активностей")
        return result

    def push_softskills_from_request(self, report: SoftskillsReport) -> MutableMapping[str, Any]:
        """ Push softskills report to SOFTSKILLS google sheet """
        worksheet = self.__get_worksheet(sheet_name="SOFTSKILLS")
        current_time = self.__get_current_time()
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

    def push_save_request_to_wiki(self, student_id: str, skill: str) -> MutableMapping[str, Any]:
        """ Push student request to WIKI_REQUESTS google sheet """
        worksheet = self.__get_worksheet(sheet_name="WIKI_REQUESTS")
        current_time = self.__get_current_time()
        result = worksheet.append_row([
            current_time,
            student_id,
            skill
        ])
        logger.debug(f'Записываем запрос студента в табличку "Все обращения к ВИКИ"')
        return result

    def push_wiki_rate(
            self, slug: str, grade: int, student_id: int = "", personalized: str = ""
    ) -> MutableMapping[str, Any]:
        """ Push student rate to WIKI_RATES google sheet """
        worksheet = self.__get_worksheet(sheet_name="WIKI_RATES")
        current_time = self.__get_current_time()
        result = worksheet.append_row([
            slug,
            student_id,
            grade,
            personalized,
            current_time
        ])
        logger.debug(f'Записываем оценку студента в табличку "Все оценки к вики "')
        return result
