import os
import gspread

from openai import AsyncOpenAI, OpenAIError, PermissionDeniedError, RateLimitError, APIConnectionError

from src.classes.ai_feedback_builder import AIFeedBackBuilder
from src.classes.checklist_builder import ChecklistBuilder
from src.classes.prompts_loader import PromptsLoader, PromptException
from src.classes.sheet_pusher import SheetPusher

# Достаем все конфиги
import src.config as config
from src.classes.wiki_loader import WikiLoader

if config.OPENAI_API_KEY is None:
    raise NameError("OPENAI_API_KEY is not set")

#  клиент для работы с таблицами
gc = gspread.service_account(filename=config.CREDENTIALS_PATH)
#  объект для отправки отчетов в гуглдоки
sheet_pusher = SheetPusher(gc, config.SHEET_IDS)

# объект для сборки критериев из таблиц
checklist_builder = ChecklistBuilder(gc, config.SHEET_IDS["INDICES"])

# объект для загрузки промптов
prompts_loader = PromptsLoader(gc, config.SHEET_IDS["PROMPTS"])

# объект для доступа в нейронке
ai_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

# объект для генерации фидбека нейроночкой
feedback_builder = AIFeedBackBuilder(ai_client, prompts_loader, sheet_pusher)

# объекд для загрузки статей
wiki_loader = WikiLoader(gc, wiki_sheet=config.SHEET_IDS["WIKI"])
