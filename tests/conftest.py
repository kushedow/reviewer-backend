import sys
import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from pathlib import Path

from faker import Faker
from httpx import AsyncClient

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..')
    )
)

load_dotenv(Path(__file__).parent.parent / '.env')

# import после добавляения в sys.path иначе не находит пути
from src.models.ai_request import AIRequest
from src.models.checklist_report import ChecklistReport
from src.models.softskills_report import SoftskillsReport

SERVER_URL = "http://127.0.0.1:8000"


@pytest.fixture
def fake():
    return Faker()


@pytest.fixture
def checklist_report(fake):
    return ChecklistReport(
        ticket_id=fake.random_number(digits=6, fix_len=True),
        student_id=fake.random_number(digits=9, fix_len=True),
        mentor_full_name=f"{fake.first_name()} {fake.last_name()}",
        stream_name="TEST / Профессия ...",
        task_name="TEST / Курсовая ...",
        checklist_data={
            str(i):
                {
                    "title": fake.sentence(nb_words=4),
                    "skill": fake.sentence(nb_words=4),
                    "grade": fake.random_int(min=1, max=5),
                    "step": 'no-step',
                    "note": 'no-note',
                } for i in range(fake.random_int(min=1, max=3))
        }
    )


@pytest.fixture
def ai_request(fake):
    return AIRequest(
        ticket_id=fake.random_number(digits=6, fix_len=True),
        mentor_full_name=f"{fake.first_name()} {fake.last_name()}",
    )


@pytest.fixture
def softskills_report(fake):
    return SoftskillsReport(
        ticket_id=fake.random_number(digits=6, fix_len=True),
        student_id=fake.random_number(digits=9, fix_len=True),
        mentor_full_name=f"{fake.first_name()} {fake.last_name()}",
        stream_name="TEST / Профессия ...",
        task_name="TEST / Курсовая ...",
        skills={
            f'skill_{i}': fake.random_int(min=1, max=5)
            for i in range(1, fake.random_int(min=2, max=6))
        }
    )


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(base_url=SERVER_URL) as client:
        yield client


@pytest.fixture
def checklist_data():
    return {
        "ticket_id": 111111,
        "student_full_name": "Глеб Кушедов",
        "mentor_full_name": "Тест Тестов",
        "stream_name": "Тестовый поток",
        "task_name": "Курсовая 6. Основы веб-разработки на Django",  # таблица где is_ready=True, status="LOADING"
    }


@pytest.fixture
def checklist_data_sheet_id():
    return {
        "ticket_id": 111111,
        "student_full_name": "Глеб Кушедов",
        "mentor_full_name": "Тест Тестов",
        "stream_name": "Тестовый поток",
        "sheet_id": "1eob4Hykpmm3S2Cigz31aPBTBNXHKbexuHq5h4h1Ehbk",
    }


@pytest.fixture
def checklist_is_ready_false_data():
    return {
        "ticket_id": 222222,
        "student_full_name": "Глеб Кушедов",
        "mentor_full_name": "Тест Тестов",
        "stream_name": "Тестовый поток",
        "task_name": "Курсовая 4. ООП",  # таблица где is_ready=False
    }


@pytest.fixture
def checklist_status_error_data():
    return {
        "ticket_id": 333333,
        "student_full_name": "Глеб Кушедов",
        "mentor_full_name": "Тест Тестов",
        "stream_name": "Тестовый поток",
        "task_name": "Курсовая 5. Работа с базами данных",  # таблица со status="ERROR"
    }


@pytest.fixture
def motivation_data_noai():
    return {
        "ticket_id": 111111,
        "student_full_name": "Глеб Кушедов",
        "mentor_full_name": "Тест Тестов",
        "stream_name": "Тестовый поток",
        "prompt_name": "NOAI",
        "feedback_body": "✅⠀Решение выложено на GitHub и находится в ветке main⠀\n✅⠀В коммитах нет "
                         "игнорируемых файлов, отлично!⠀\n✅⠀Создан .gitignore файл, использован шаблон "
                         "для заполнения (например, этот: "
                         "https://github.com/github/gitignore/blob/main/Python.gitignore)⠀\n</p><p><strong>"
                         "Соотетствие pep 8: </strong></p><p>\n✅⠀Нет грубых нарушений PEP8 в оформлении кода⠀\n</p>"
                         "<p><strong>Класс категории: </strong></p><p>\n✅⠀В случае, если количество в товаре - "
                         "нулевое происходит выбрасывание ошибки ValueError с соответсвующим сообщением. Сообщение "
                         "при выбрасывании ошибки переопределено и сообщает пользователю о том, что из-за чего "
                         "произошла ошибка (например, \"Нельзя добавить товар с нулевым количеством!\")⠀\n✅⠀"
                         "В классе категории реализован метод, который работает с приватным атрибутом списка товаров. "
                         "Метод расчитывает среднюю стоимость с помощью функций sum() и len() ⠀\n✅⠀Метод подсчета "
                         "среднего ценника возвращает верные значения⠀\n✅⠀Обработан случай, когда в категории нет "
                         "товаров и сумма всех товаров будет делиться на ноль. Метод подсчета среднего ценника "
                         "возвращает 0, когда количество товаров в категории равно 0. Ошибки деления на ноль не "
                         "возникает.⠀\n✅⠀При нулевом количестве продуктов обрабатывается исключение ZeroDivisionError"
                         " ⠀\n✅⠀При нулевом количестве товаров программа продолжает работу⠀",
        "task_name": "Тест 1"
    }


@pytest.fixture
def motivation_data_simple():
    return {
        "ticket_id": 111111,
        "student_full_name": "Глеб Кушедов",
        "mentor_full_name": "Тест Тестов",
        "stream_name": "Тестовый поток",
        "prompt_name": "python_simple",
        "feedback_body": "✅⠀Решение выложено на GitHub и находится в ветке main⠀\n✅⠀В коммитах нет "
                         "игнорируемых файлов, отлично!⠀\n✅⠀Создан .gitignore файл, использован шаблон "
                         "для заполнения (например, этот: "
                         "https://github.com/github/gitignore/blob/main/Python.gitignore)⠀\n</p><p><strong>"
                         "Соотетствие pep 8: </strong></p><p>\n✅⠀Нет грубых нарушений PEP8 в оформлении кода⠀\n</p>"
                         "<p><strong>Класс категории: </strong></p><p>\n✅⠀В случае, если количество в товаре - "
                         "нулевое происходит выбрасывание ошибки ValueError с соответсвующим сообщением. Сообщение "
                         "при выбрасывании ошибки переопределено и сообщает пользователю о том, что из-за чего "
                         "произошла ошибка (например, \"Нельзя добавить товар с нулевым количеством!\")⠀\n✅⠀"
                         "В классе категории реализован метод, который работает с приватным атрибутом списка товаров. "
                         "Метод расчитывает среднюю стоимость с помощью функций sum() и len() ⠀\n✅⠀Метод подсчета "
                         "среднего ценника возвращает верные значения⠀\n✅⠀Обработан случай, когда в категории нет "
                         "товаров и сумма всех товаров будет делиться на ноль. Метод подсчета среднего ценника "
                         "возвращает 0, когда количество товаров в категории равно 0. Ошибки деления на ноль не "
                         "возникает.⠀\n✅⠀При нулевом количестве продуктов обрабатывается исключение ZeroDivisionError"
                         " ⠀\n✅⠀При нулевом количестве товаров программа продолжает работу⠀",
        "task_name": "Тест 1"
    }


@pytest.fixture
def report_data():
    return {
        "ticket_id": 600111,
        "student_id": 111222333,
        "student_full_name": "Глеб Кушедов",
        "mentor_full_name": "Тест Тестов",
        "stream_name": "Python 01",
        "task_name": "Тестовое задание",
        "checklist_data": {
            "0": {
                "criteria": "Решение выложено на GitHub",
                "grade": "5",
                "group": "Работа с git",
                "note": "no-note",
                "skill": "Рабочий процесс (git status, add, commit)",
                "step": "no-step",
                "title": "Решение выложено на GitHub"
            },
            "1": {
                "criteria": "В коммиты не добавлены игнорируемые файлы ",
                "grade": "5",
                "group": "Работа с git",
                "note": "no-note",
                "skill": "Рабочий процесс (git status, add, commit)",
                "step": "no-step",
                "title": "В коммиты не добавлены игнорируемые файлы "
            },
            "2": {
                "criteria": "В проекте есть .gitignore",
                "grade": "5",
                "group": "Работа с git",
                "note": "no-note",
                "skill": "Файл .gitignore",
                "step": "no-step",
                "title": "В проекте есть .gitignore"
            }
        }
    }


@pytest.fixture
def report_soft_skills_data():
    return {
        "ticket_id": 600101,
        "student_id": 111222333,
        "student_full_name": "Иван Тапорыжкин",
        "mentor_full_name": "Тест Тестов",
        "stream_name": "Python 11.0",
        "task_name": "Домашка тестовая 1.1",
        "skills": {
            "skill_1": 1,
            "skill_2": 1,
            "skill_3": 2,
            "skill_4": 0
        }
    }
