from openai import AsyncOpenAI, OpenAIError

from src.classes.ai_pusher import AIPusher
from src.classes.prompts_loader import PromptsLoader
from src.models.AIRequest import AIRequest


class AIFeedBackBuilder:
    """
    Генерируем мотивирующую обратную связь на основе написанного фидбека и таблицы с промптами
    """

    def __init__(self, ai_client: AsyncOpenAI, prompts_loader: PromptsLoader, pusher: AIPusher):
        self.__ai_client = ai_client
        self.__prompts_loader = prompts_loader
        self.__pusher = pusher

    async def _make_request(self, prompt):
        """Выполняем запрос к нейронке по готовому промпту"""
        completion = await self.__ai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": prompt}]
        )

        response = completion.choices[0].message.content

        return response

    def _buildPrompt(self, ai_request: AIRequest) -> str:
        """Собираем промпт для нейронки на основе"""
        prompt_template: str = self.__prompts_loader.get(ai_request.prompt_name)
        student_first_name: str = ai_request.student_full_name.split(" ")[0]
        feedback_body: str = ai_request.feedback_body

        prompt: str = f"{prompt_template} \n Имя ученика: {student_first_name} \n <НАЧАЛО>\n {feedback_body} \n</КОНЕЦ>"
        return prompt


    async def build(self, ai_request: AIRequest):
        """Интерфейс для обработки запроса на мотивирующий фидбек:
        Высасывает шаблон промпта по его названию с помощью prompt_loader
        Собирает промпт из объекта запроса
        Генерирует ответ с помощью __ai_client
        Логирует запрос в табличку с помощью AIPusher
        """
        prompt = self._buildPrompt(ai_request)
        response = await self._make_request(prompt)
        self.__pusher.push(ai_request, response)
        return response
