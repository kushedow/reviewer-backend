from gspread import Client, Worksheet, Spreadsheet


class SheetLoader:

    def __init__(self, g_client, sheet_ids):
        self.__google_client: Client = g_client
        self.__sheet_ids: dict[str, str] = sheet_ids

    def get_last_n_rows(self, sheet_name: str, rows_count: int, worksheet_name: str | None = None):
        sheet_id = self.__sheet_ids[sheet_name]
        sheet: Spreadsheet = self.__google_client.open_by_key(sheet_id)
        if worksheet_name:
            worksheet: Worksheet = sheet.worksheet(worksheet_name)
        else:
            worksheet: Worksheet = sheet.get_worksheet(0)
        all_values = worksheet.get_all_values()
        return all_values[-rows_count:]