from gspread import Spreadsheet, Client
from gspread.worksheet import Worksheet
from loguru import logger

class PromptException(Exception):
    pass

class PromptsLoader:

    def __init__(self, g_client, sheet_id):
        self.__google_client: Client = g_client
        self.__sheet_id: str = sheet_id
        self.__worksheet: Worksheet | None = None

        self.reload()

    def reload(self) -> None:
        file = self.__google_client.open_by_key(self.__sheet_id)
        self.__worksheet = file.get_worksheet(0)

    def list(self) -> list[str]:
        """
        Возвращает список всех доступных название промптов
        :return:
        """
        first_column_values = self.__worksheet.col_values(1)
        return first_column_values[1:]

    def get(self, name: str) -> str:
        """
        Получает промпт по имени
        """
        try:
            cell = self.__worksheet.find(name, in_column=1)
            prompt_value = self.__worksheet.row_values(cell.row)[1]
            return prompt_value
        except (ValueError, AttributeError):
            raise PromptException(f"Не удалось загрузить промпт по такому имени: {name}")
