import random

from openai import AsyncOpenAI, OpenAIError

from src.classes.prompts_loader import PromptsLoader
from src.classes.sheet_pusher import SheetPusher
from src.models.ai_request import AIRequest
from samples.motivation_temp import review_motivation


class AIFeedBackBuilder:
    """
    Генерируем мотивирующую обратную связь на основе написанного фидбека и таблицы с промптами
    """

    def __init__(self, ai_client: AsyncOpenAI, prompts_loader: PromptsLoader, pusher: SheetPusher):
        self.__ai_client = ai_client
        self.__prompts_loader = prompts_loader
        self.__pusher: SheetPusher = pusher

    async def _make_request(self, prompt):
        """Выполняем запрос к нейронке по готовому промпту"""
        completion = await self.__ai_client.chat.completions.create(
            model="gpt-4", temperature=0.1, messages=[{"role": "user", "content": prompt}]
        )

        response = completion.choices[0].message.content

        return response

    def _build_prompt(self, ai_request: AIRequest) -> str:
        """Собираем промпт для нейронки на основе"""
        prompt_template: str = self.__prompts_loader.get(ai_request.prompt_name)
        student_first_name: str = ai_request.student_full_name.split(" ")[0]
        feedback_body: str = ai_request.feedback_body

        prompt: str = f"{prompt_template} \n Имя ученика: {student_first_name} \n <НАЧАЛО>\n {feedback_body} \n</КОНЕЦ>"
        return prompt

    def _get_grade_from_review(self, feedback_body):

        red_count = feedback_body.count("❌")
        yellow_count = feedback_body.count("✴️")

        if red_count > 3:
            return 2
        if red_count > 0:
            return 3
        if yellow_count > 0:
            return 4
        return 5

    async def build(self, ai_request: AIRequest):
        """Интерфейс для обработки запроса на мотивирующий фидбек:
        Высасывает шаблон промпта по его названию с помощью prompt_loader
        Собирает промпт из объекта запроса
        Генерирует ответ с помощью __ai_client
        Логирует запрос в табличку с помощью AIPusher
        """

        first_name = ai_request.student_full_name.split(" ")[0]

        if ai_request.prompt_name == "NOAI":
            grade = self._get_grade_from_review(ai_request.feedback_body)
            motivation_items = review_motivation[grade]

            # prompt = f"Представь, что ты преподаватель, который проверяет работу ученика.  " \
            #          f"Возьми за основу текст между <начало> и <конец> и дополни текст, выполнив условия" \
            #          f"1 Тебя зовут: {ai_request.mentor_full_name}, ученика зовут: {ai_request.student_full_name}" \
            #          f"2 Начни с 'привет', обратившись к ученику по имени (без фамилии)." \
            #          f"3 Сохрани символы '///' " \
            #          f"4 Не указывай свое имя в работе " \
            #          f"5 Определи пол преподавателя по имени: {ai_request.mentor_full_name}" \
            #          f"Если он женский, пиши от лица женщины, если нет – от лица мужчины" \
            #          f"5 Определи пол ученика по имени: {ai_request.student_full_name}" \
            #          f"Если он женский, ставь окончания так, как пишешь женщине, если нет – как пишешь мужчине" \
            #          f"7 Обязательно учитывай гендер фамилии ученика при написании текста " \
            #          f"8 Не включай теги <начало><конец> в результат" \
            #          f"<начало>{random.choice(motivation_items)} <конец> "

            prompt = f"Имя преподавателя: {ai_request.mentor_full_name}" \
                     f"Имя ученика: {ai_request.student_full_name}" \
                     f"Шаг 1: определи пол преподавателя и ученика " \
                     f"Шаг 2: С учетом пола доработай текст:" \
                     f"<начало>Привет, <имя ученика>! \n {random.choice(motivation_items)} <конец> " \
                     f"В ответе должен быть только результат выполнения шага 2" \
                     f"В ответе мы называем ученика по имени только 1 раз" \
                     f"В ответе мы НЕ имя преподавателя" \
                     f"Текст может быть перефразирован" \
                     f"В ответе должен сохраниться символ ///"

            response = await self._make_request(prompt)
            return response

        prompt = self._build_prompt(ai_request)
        response = await self._make_request(prompt)
        self.__pusher.push_ai_generation_from_request(ai_request, response)
        return response
