import asyncio
import json

from openai import AsyncOpenAI

task = """
1. Сперва программа здоровается и предлагает начать:
`Привет! Предлагаю проверить свои знания английского! 
 Расскажи, как тебя зовут!`

2. Программа считывает имя пользователя и говорит:
Привет, `{имя пользователя}`, начинаем тренировку!
---
3. Программа задает по очереди три вопроса: 
Вопрос: `My name ___ Vova`
Верный ответ: `is`

Вопрос: `I ___ a coder`
Верный ответ: `am`

Вопрос: `I live ___ Moscow`
Верный ответ: `in`

Если ответ правильный, приложение говорит: 

`Ответ верный!` 
`Вы получаете 10 баллов!`

Если нет, говорит: 
`Неправильно.` 
`Правильный ответ: ______`

Затем приложение задает следующий вопрос.

---

4. После ответа на 3 вопроса приложение говорит:
`Вот и все, {имя пользователя}! 
 Вы ответили на {___} вопросов из 3 верно.`
`Вы заработали {___} баллов.
 Это {____} процентов.`
"""

user_solution = """
#Пользователь вводит свое имя
user_name = input()
#Начало выполнения задания
print(f"Привет, {user_name}, начинаем тренировку!")
#Вводим переменные вопросов и счетчика
question_1 = "My name _ Vova."
question_2 = "I _ coder."
question_3 = "I live _ Moscow."
counter = 0
#Вопросы пользователю
#Вопрос 1
print(question_1)
question_1 = input()

if question_1 == "is":
    counter += 10
    print("Ответ верный! Вы получаете 10 баллов")
else :
    print("Неправильно. \nВерный ответ: is \nВы получаете 0 баллов")
#Вопрос 2
print(question_2)
question_2 = input()

if question_2 == "am":
    counter += 10
    print("Ответ верный! Вы получаете 10 баллов")
else:
    print("Неправильно. \nВерный ответ: am \nВы получаете 0 баллов")

#Расчеты баллов и проценты
correct_answers = counter // 10 #Правильные ответы
percent = round(counter/3*10) #Проценты
#Условия для изменения окончаний
#Если 1 верный ответ, то пишем процента
#Если 0 правильных ответов, то строчку с процентами не выводим и изменяем окончания
if percent == 33:
    print(f"Вот и все, {user_name} ! Вы ответили на {correct_answers} вопрос из 3 верно. \nВы заработали {counter} баллов. \nЭто {percent} процента")
elif percent == 0:
    print(f"Вот и все, {user_name} ! Вы ответили на {correct_answers} вопросов из 3 верно. \nПопробуйте снова! ")
else:
    print(f"Вот и все, {user_name} ! Вы ответили на {correct_answers} вопроса из 3 верно. \nВы заработали {counter} баллов. \nЭто {percent} процентов")
"""

instruction = f"""
Начало инструкции:
У нас есть задание, которое ученик должен был выполнить:
{task}
Сейчас я передам тебе решение ученика между тегами <начало> <конец> .
<начало>
{user_solution}
<конец>
Конец инструкции, ответь OK            
"""


class AIChecker:

    def __init__(self, ai_client):
        self.ai_client: AsyncOpenAI = ai_client
        self.assistant_id = "asst_yffneQz9MGXWvkNutXcnux53"

    def get_checklist(self):
        criteria_file = open("samples/sample_criteria.json")
        data = json.load(criteria_file)
        return data

    async def open_thread(self, message):

        self.thread = await self.ai_client.beta.threads.create()

        await self.ai_client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message
        )

        return await self.fetch_answer()

    async def fetch_answer(self):

        run = await self.ai_client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant_id
        )

        while run.status != 'completed':
            run = await self.ai_client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=run.id)
            await asyncio.sleep(1)

        messages = await self.ai_client.beta.threads.messages.list(thread_id=self.thread.id)
        answer = messages.model_dump()["data"][0]["content"][0]["text"]["value"]

        return answer

    async def continue_thread(self, message):

        await self.ai_client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message
        )

        return await self.fetch_answer()

    async def run_assistant(self):

        answer_1 = await self.open_thread(instruction)
        print(answer_1)

        checklist = self.get_checklist()

        for checkbox in list(checklist.values()):
            point_prompt = f"Ответь True, если верно утверждение \"{checkbox}\". Ответь False, если неверно"
            answer_check = await self.continue_thread(point_prompt)

            if answer_check == "False":
                point_fix_prompt = f"Объясни в пару предложений, что нужно исправить в коде, чтобы было выполнено условие \"{checkbox}\""
                point_fix_answers = await self.continue_thread(point_fix_prompt)
                checkbox["grade"] = 3
                checkbox["note"] = point_fix_answers
            else:
                checkbox["grade"] = 5

            print(checkbox["title"], checkbox["grade"], "\n", checkbox.get("note"))
