from gspread import GSpreadException, SpreadsheetNotFound
from gspread_asyncio import (
    AsyncioGspreadClientManager,
    AsyncioGspreadClient,
    AsyncioGspreadWorksheet,
    AsyncioGspreadSpreadsheet
)
from loguru import logger

from src.classes.abc_gspread_loader import ABCGspreadLoader
from src.models.checklist import Checklist, ChecklistStatusEnum


class ChecklistBuilder(ABCGspreadLoader):

    def __init__(self, async_manager, index_sheet):

        self.__async_manager: AsyncioGspreadClientManager = async_manager
        self.__async_client: AsyncioGspreadClient | None = None
        self.__index_sheet = index_sheet
        self.__cache: dict[str, Checklist] = {}

    async def _load_indices(self):

        file = await self.__async_client.open_by_key(self.__index_sheet)
        sheet = await file.worksheet("index")
        records = await sheet.get_all_records()
        self.__cache = {record["lesson"]: Checklist(**record) for record in records}

    async def _load_one_checklist(self, index: int, checklist: Checklist):

        try:

            file: AsyncioGspreadSpreadsheet = await self.__async_client.open_by_key(checklist.sheet_id)
            sheet: AsyncioGspreadWorksheet = await file.get_sheet1()
            data: list[dict] = await sheet.get_all_records()

            if len(data) == 0 or "title" not in data[0].keys():
                raise KeyError

            checklist.body = data
            checklist.status = ChecklistStatusEnum.OK
            checklist.is_ready = True
            logger.debug(f"Processed checklist {index} of {len(self.__cache)}")

        except (GSpreadException, SpreadsheetNotFound, KeyError):
            logger.error(f"Checklist {checklist.lesson} {checklist.sheet_id} loading error")
            checklist.status = ChecklistStatusEnum.ERROR

    async def _load_checklists(self):

        for index, checklist in enumerate(self.__cache.values(), start=1):
            await self._load_one_checklist(index, checklist)

    def get(self, lesson_name) -> Checklist | None:
        lesson_name = lesson_name.strip().rstrip(".")
        return self.__cache.get(lesson_name)

    def find(self, key, value) -> Checklist | None:
        for checklist in self.__cache.values():
            if getattr(checklist, key) == value:
                return checklist

    async def reload(self):

        self.__async_client = await self.__async_manager.authorize()

        logger.info(f"{self.__class__.__name__}: Caching started")

        await self._load_indices()
        await self._load_checklists()

        logger.info(f"{self.__class__.__name__}: Caching completed")
