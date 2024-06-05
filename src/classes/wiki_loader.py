from gspread import Client
from loguru import logger


class WikiLoader:

    SKILL_COLUMN = 2

    def __init__(self, g_client: Client, wiki_sheet: str = ""):

        self.__google_client: Client = g_client
        self.__wiki_sheet: str = wiki_sheet
        file = self.__google_client.open_by_key(self.__wiki_sheet)
        self.__worksheet = file.get_worksheet(0)

    def load_wiki_by_skill(self, skill):

        header = self.__worksheet.row_values(1)

        try:
            cell = self.__worksheet.find(skill.strip(), in_column=self.SKILL_COLUMN)

            if cell:
                row_values = self.__worksheet.row_values(cell.row)

                wiki_data = dict(zip(header, row_values))
                logger.debug(f"Загружена статья")
                logger.debug(wiki_data)
                return wiki_data["article"]
            else:
                logger.debug(f"Статья не найдена")
                raise KeyError("Статья не найдена")

        except (ValueError, AttributeError, IndexError) as error:
            logger.debug(f"Произошла ошибка {str(error)}")
            raise ValueError(f"Не удалось загрузить статью по такому названию: {skill}, {str(error)}")
