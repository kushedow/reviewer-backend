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

    def __init__(self, async_manager, index_sheet, critical_headers, noncritical_headers):

        self.__async_manager: AsyncioGspreadClientManager = async_manager
        self.__async_client: AsyncioGspreadClient | None = None
        self.__index_sheet = index_sheet
        self.__cache: dict[str, Checklist] = {}
        self.__critical_headers = critical_headers
        self.__noncritical_headers = noncritical_headers

    async def _load_indices(self):

        file = await self.__async_client.open_by_key(self.__index_sheet)
        sheet = await file.worksheet("index")
        records = await sheet.get_all_records()
        try:
            self.__cache = {
                str(record["lesson"]): Checklist(**{**record, "lesson": str(record["lesson"])})
                for record in records
            }
        except Exception as e:
            logger.error(e)

    @staticmethod
    async def _load_advices(file: AsyncioGspreadSpreadsheet):

        try:
            sheet = await file.worksheet("advices")
            return await sheet.get_all_records()
        except GSpreadException:
            logger.error(f"Checklist advices loading error")
            return None

    async def _check_headers(self, sheet_data: list[dict]):
        headers_in_sheet = set(sheet_data[0].keys())

        if missing_critical_headers := self.__critical_headers - headers_in_sheet:
            raise KeyError(f"Critical header(s) {missing_critical_headers} not found")

        if missing_noncritical_headers := self.__noncritical_headers - headers_in_sheet:
            logger.warning(f"Noncritical header(s) {missing_noncritical_headers} not found")

    async def _load_one_checklist(self, index: int, checklist: Checklist):

        try:
            file: AsyncioGspreadSpreadsheet = await self.__async_client.open_by_key(checklist.sheet_id)
            sheet: AsyncioGspreadWorksheet = await file.get_sheet1()
            data: list[dict] = await sheet.get_all_records()

            await self._check_headers(data)

            if len(data) == 0 or "title" not in data[0].keys():
                raise KeyError

            all_worksheets = await file.worksheets()
            if 'advices' in [sheet.title for sheet in all_worksheets]:
                if advices := await self._load_advices(file):
                    checklist.advices = advices

            checklist.body = data
            checklist.status = ChecklistStatusEnum.OK

            logger.debug(f"Processed checklist {index} of {len(self.__cache)}")

        except (GSpreadException, SpreadsheetNotFound, KeyError) as e:
            logger.error(f"Checklist {checklist.lesson} {checklist.sheet_id} loading error {str(e)}")
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
