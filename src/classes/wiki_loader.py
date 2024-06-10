from gspread import Client
from loguru import logger

from src.models.wiki_article import WikiArticle


class WikiLoader:

    SKILL_COLUMN = 2
    __cache = {}

    def __init__(self, g_client: Client, wiki_sheet: str = ""):

        self.__google_client: Client = g_client
        self.__wiki_sheet: str = wiki_sheet
        document = self.__google_client.open_by_key(self.__wiki_sheet)
        self.__worksheet = document.get_worksheet(0)

        # Загружаем и кешируем все статьи
        self.reload()

    def load_wiki_by_skill(self, slug):

        article: WikiArticle = self.__cache.get(slug)

        if article is None:
            logger.debug(f"Не удалось загрузить статью {slug}")
            raise KeyError(f"Не удалось загрузить статью по такому названию: {slug}")

        return article

    def reload(self):

        sheet = self.__worksheet
        records = sheet.get_all_records()
        self.__cache = {record["slug"]: WikiArticle(**record) for record in records}

