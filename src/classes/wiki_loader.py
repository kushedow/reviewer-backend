from gspread import Client
from loguru import logger

from src.classes.abc_gspread_loader import ABCGspreadLoader
from src.models.wiki_article import WikiArticle


class WikiLoader(ABCGspreadLoader):

    SKILL_COLUMN = 2
    __cache = {}

    def __init__(self, g_client: Client, wiki_sheet: str = ""):

        self.__google_client: Client = g_client
        self.__wiki_sheet: str = wiki_sheet

    def get(self, slug):

        article: WikiArticle = self.__cache.get(slug)

        if article is None:
            logger.debug(f"Не удалось загрузить статью {slug}")
            raise KeyError(f"Не удалось загрузить статью по такому названию: {slug}")

        return article

    def find(self, key: str, value: str | int | float):
        value = value.strip().rstrip(".")
        for article in self.__cache.values():
            if getattr(article, key).strip().rstrip(".") == value:
                return article

    def reload(self):

        document =  self.__google_client.open_by_key(self.__wiki_sheet)
        sheet = document.get_worksheet(0)

        logger.info(f"{self.__class__.__name__}: Caching started")
        records = sheet.get_all_records()
        self.__cache = {record["slug"]: WikiArticle(**record) for record in records}
        logger.info(f"{self.__class__.__name__}: Caching completed")

