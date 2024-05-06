from gspread import Client, Spreadsheet, Worksheet


class StatsManager:
    """Извлекает статистику из заполненных таблиц и отдает в понятном виде"""

    def __init__(self, g_client: Client, sheet_ids: dict[str, str]):
        self.__google_client: Client = g_client
        self.__sheet_id: str = sheet_ids.get("CRITERIA")

    def get_student_skills(self, student_id):

        sheet: Spreadsheet = self.__google_client.open_by_key(self.__sheet_id)
        worksheet: Worksheet = sheet.worksheet("criteria")

        cells = worksheet.findall(str(student_id), in_column=1)

        rows = []
        for cell in cells:
            # Fetch the whole row where the match is found
            row_values = worksheet.row_values(cell.row)
            rows.append(row_values)

        return rows




