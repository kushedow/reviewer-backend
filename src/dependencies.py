import asyncio
import os
import gspread
import gspread_asyncio
from google.oauth2.service_account import Credentials

from openai import AsyncOpenAI

from src.classes.ai_feedback_builder import AIFeedBackBuilder
from src.classes.checklist_builder import ChecklistBuilder
from src.classes.prompts_loader import PromptsLoader, PromptException
from src.classes.sheet_pusher import SheetPusher

# Достаем все конфиги
import src.config as config
from src.classes.skillset import SkillSet
from src.classes.wiki_ai_booster import WikiAIBooster
from src.classes.wiki_loader import WikiLoader

if config.OPENAI_API_KEY is None:
    raise NameError("OPENAI_API_KEY is not set")

#  клиент для работы с таблицами
gc = gspread.service_account(filename=config.CREDENTIALS_PATH)

async_gspread_manager = gspread_asyncio.AsyncioGspreadClientManager(config.get_creds)

#  объект для отправки отчетов в гуглдоки
sheet_pusher = SheetPusher(gc, config.SHEET_IDS)

# объект для сборки критериев из таблиц
checklist_builder = ChecklistBuilder(async_gspread_manager, config.SHEET_IDS["INDICES"])

# объект для загрузки промптов
prompts_loader = PromptsLoader(gc, config.SHEET_IDS["PROMPTS"])

# объект для доступа в нейронке
ai_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

# объект для генерации фидбека нейроночкой
feedback_builder = AIFeedBackBuilder(ai_client, prompts_loader, sheet_pusher)

# объект для загрузки статей
wiki_loader = WikiLoader(gc, wiki_sheet=config.SHEET_IDS["WIKI"])

# Объект для докручивание статей с персонализацией
wiki_ai_booster = WikiAIBooster(ai_client)

# Создаем скиллсет, который связывает чеклисты и навыки в вики
skillset = SkillSet(wiki_loader, checklist_builder)

async def reload_cache():

    wiki_loader.reload()
    prompts_loader.reload()
    await checklist_builder.reload()
