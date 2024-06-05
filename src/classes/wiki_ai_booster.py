from openai import  AsyncClient

PERSONAL_PROMPT = "Перепиши эту статью на русском языке для ученика учетом того, что:" \
                  "Ее уровень английского – низкий" \
                  "Она работает домохозяйкой с 2 детьми, примеры нужно заменить, взять из ее профессиональной области" \
                  "Ей 23 года." \
                  "Статья:" \
                  "" \

class WikiAIBooster:

    def __init__(self, ai_client: AsyncClient):

        self.__ai_client = ai_client


    async def _make_request(self, prompt):

        """Выполняем запрос к нейронке по готовому промпту"""
        completion = await self.__ai_client.chat.completions.create(
            model="gpt-4o", temperature=0.1, messages=[{"role": "user", "content": prompt}]
        )

        response = completion.choices[0].message.content

        return response

    async def improve(self, article_content: str, student_data=None):

        if student_data is None:
            student_data = dict()

        prompt = PERSONAL_PROMPT + article_content
        result = await self._make_request(prompt)
        return result




