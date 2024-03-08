from gspread import Spreadsheet, Client
from gspread.worksheet import JSONResponse, Worksheet

from classes.SkillRecord import SkillRecord
from gspread.exceptions import GSpreadException, SpreadsheetNotFound, APIError

from exceptions.SkillApiError import  SkillApiError


class SkillPusher:

    def __init__(self, g_client, sheet_id):
        self.__google_client: Client = g_client
        self.__sheet_id: str = sheet_id

    def push(self, list_of_records: list[SkillRecord]):

        if not list_of_records:
            raise ValueError("Cписок критериев для добавления пуст")

        data_to_push = []
        for record in list_of_records:
            data_to_push.append([
                record.ticket_id,
                record.skill,
                record.grade,
            ])

        try:
            document: Spreadsheet = self.__google_client.open_by_key(self.__sheet_id)
            sheet: Worksheet = document.get_worksheet(0)
            result: JSONResponse = sheet.append_rows(data_to_push)

        except SpreadsheetNotFound as e:
            raise SkillApiError(f"Таблица для вставки скиллов не найдена: {e}")

        except PermissionError as e:
            raise SkillApiError(f"К таблице для вставки скиллов нет доступа: {e}")

        except (APIError, GSpreadException) as e:
            raise SkillApiError(f"Какая-то ошибка с апи гугл-таблиц: {e}")

        return result


