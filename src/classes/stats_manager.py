from gspread import Client, Spreadsheet, Worksheet

STUDENT_ID_COLUMN_NUMBER = 2

class StatsManager:
    """Извлекает статистику из заполненных таблиц и отдает в понятном виде"""

    def __init__(self, g_client: Client, sheet_ids: dict[str, str]):
        self.__google_client: Client = g_client
        self.__sheet_id: str = sheet_ids.get("CRITERIA")

    def get_all_student_rows(self, student_id):

        sheet: Spreadsheet = self.__google_client.open_by_key(self.__sheet_id)
        worksheet: Worksheet = sheet.worksheet("criteria")

        cells = worksheet.findall(str(student_id), in_column=STUDENT_ID_COLUMN_NUMBER)

        rows = []
        for cell in cells:
            # Fetch the whole row where the match is found
            row_values = worksheet.row_values(cell.row)
            row_values = worksheet.findall()
            rows.append(row_values)

        return rows

    def get_all_student_skills(self, student_id):

        student_skills = {}

        all_student_rows = self.get_all_student_rows(student_id)

        for one_row in all_student_rows:

            pass




