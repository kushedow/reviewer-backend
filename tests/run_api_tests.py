import json

import pytest
import requests

SERVER_URL = "http://0.0.0.0:80/"


class TestRefresh:

    def test_refresh(self):
        response = requests.get(SERVER_URL + "refresh")
        assert response.status_code == 200, "Status code is not 200"


# /version

class TestVersion:

    def test_version(self):
        response = requests.get(SERVER_URL + "version")
        assert response.status_code == 200, "Status code is not 200"
        result_data = response.json()
        assert isinstance(result_data, dict)
        assert result_data.get("frontend__min_version") is not None


#   _______    _______        ___     ____    ____   _______    _________    ______
#  |_   __ \  |_   __ \     .'   `.  |_   \  /   _| |_   __ \  |  _   _  | .' ____ \
#    | |__) |   | |__) |   /  .-.  \   |   \/   |     | |__) | |_/ | | \_| | (___ \_|
#    |  ___/    |  __ /    | |   | |   | |\  /| |     |  ___/      | |      _.____`.
#   _| |_      _| |  \ \_  \  `-'  /  _| |_\/_| |_   _| |_        _| |_    | \____) |
#  |_____|    |____| |___|  `.___.'  |_____||_____| |_____|      |_____|    \______.'


class TestPrompts:

    def test_get_all_prompts(self):
        response = requests.get(SERVER_URL + "prompts")
        assert response.status_code == 200, "Status code is not 200"
        assert isinstance(response.json(), list), "Response body is not a list"

    def test_get_existing_prompt(self):
        response = requests.get(SERVER_URL + "prompts/NOAI")
        assert response.status_code == 200, "Status code is not 200"
        assert isinstance(response.json(), str), "Response body is not a string"

    def test_get_non_existing_prompt(self):
        response = requests.get(SERVER_URL + "prompts/nonexisting")
        assert response.status_code == 404, "Status code is not 404"


# /checklist

class TestChecklist:
    request = {
        "ticket_id": 111111,
        "student_full_name": "Глеб Кушедов",
        "mentor_full_name": "Слава Леонтьев",
        "stream_name": "Тестовый поток",
        "task_name": "13.1 Введение в ООП"
    }

    keys = {"3", "4", "5", "title", "group", "step", "skill", "hint", "comments"}

    def test_existing_checklist(self):
        headers = {"Content-Type": "application/json"}
        response = requests.post(SERVER_URL + "checklist", data=json.dumps(self.request), headers=headers)

        assert response.status_code == 200, "Status code is not 200"
        result_data = response.json()
        assert isinstance(result_data, list)
        result_data_keys = set(result_data[0].keys())
        assert result_data_keys == self.keys


# /generate-motivation

class TestGenerateMotivation:
    request = {
        "ticket_id": 111111,
        "student_full_name": "Глеб Кушедов",
        "mentor_full_name": "Слава Леонтьев",
        "stream_name": "Тестовый поток",
        "prompt_name": "NOAI",
        "feedback_body": "✅⠀Решение выложено на GitHub и находится в ветке main⠀\n✅⠀В коммитах нет игнорируемых файлов, отлично!⠀\n✅⠀Создан .gitignore файл, использован шаблон для заполнения (например, этот: https://github.com/github/gitignore/blob/main/Python.gitignore)⠀\n</p><p><strong>Соотетствие pep 8: </strong></p><p>\n✅⠀Нет грубых нарушений PEP8 в оформлении кода⠀\n</p><p><strong>Класс категории: </strong></p><p>\n✅⠀В случае, если количество в товаре - нулевое происходит выбрасывание ошибки ValueError с соответсвующим сообщением. Сообщение при выбрасывании ошибки переопределено и сообщает пользователю о том, что из-за чего произошла ошибка (например, \"Нельзя добавить товар с нулевым количеством!\")⠀\n✅⠀В классе категории реализован метод, который работает с приватным атрибутом списка товаров. Метод расчитывает среднюю стоимость с помощью функций sum() и len() ⠀\n✅⠀Метод подсчета среднего ценника возвращает верные значения⠀\n✅⠀Обработан случай, когда в категории нет товаров и сумма всех товаров будет делиться на ноль. Метод подсчета среднего ценника возвращает 0, когда количество товаров в категории равно 0. Ошибки деления на ноль не возникает.⠀\n✅⠀При нулевом количестве продуктов обрабатывается исключение ZeroDivisionError ⠀\n✅⠀При нулевом количестве товаров программа продолжает работу⠀",
        "task_name": "Тест 1"
    }

    request_ai = {
        "ticket_id": 111111,
        "student_full_name": "Глеб Кушедов",
        "mentor_full_name": "Слава Леонтьев",
        "stream_name": "Тестовый поток",
        "prompt_name": "python_simple",
        "feedback_body": "✅⠀Решение выложено на GitHub и находится в ветке main⠀\n✅⠀В коммитах нет игнорируемых файлов, отлично!⠀\n✅⠀Создан .gitignore файл, использован шаблон для заполнения (например, этот: https://github.com/github/gitignore/blob/main/Python.gitignore)⠀\n</p><p><strong>Соотетствие pep 8: </strong></p><p>\n✅⠀Нет грубых нарушений PEP8 в оформлении кода⠀\n</p><p><strong>Класс категории: </strong></p><p>\n✅⠀В случае, если количество в товаре - нулевое происходит выбрасывание ошибки ValueError с соответсвующим сообщением. Сообщение при выбрасывании ошибки переопределено и сообщает пользователю о том, что из-за чего произошла ошибка (например, \"Нельзя добавить товар с нулевым количеством!\")⠀\n✅⠀В классе категории реализован метод, который работает с приватным атрибутом списка товаров. Метод расчитывает среднюю стоимость с помощью функций sum() и len() ⠀\n✅⠀Метод подсчета среднего ценника возвращает верные значения⠀\n✅⠀Обработан случай, когда в категории нет товаров и сумма всех товаров будет делиться на ноль. Метод подсчета среднего ценника возвращает 0, когда количество товаров в категории равно 0. Ошибки деления на ноль не возникает.⠀\n✅⠀При нулевом количестве продуктов обрабатывается исключение ZeroDivisionError ⠀\n✅⠀При нулевом количестве товаров программа продолжает работу⠀",
        "task_name": "Тест 1"
    }

    def test_generate_motivation_low_ai(self):
        headers = {"Content-Type": "application/json"}
        response = requests.post(SERVER_URL + "generate-motivation", data=json.dumps(self.request), headers=headers)
        assert response.status_code == 200, "Status code is not 200"
        response_data = response.json()
        assert isinstance(response_data, dict)
        response_text = response_data.get("response")
        assert response_text is not None
        assert "Глеб" in response_text

    def test_generate_motivation_ai(self):
        headers = {"Content-Type": "application/json"}
        response = requests.post(SERVER_URL + "generate-motivation", data=json.dumps(self.request_ai), headers=headers)
        assert response.status_code == 200, "Status code is not 200"
        response_data = response.json()
        assert isinstance(response_data, dict)
        response_text = response_data.get("response")
        assert response_text is not None
        assert "Глеб" in response_text


class TestReports:
    report_criteria_data = {
        "ticket_id": 600111,
        "student_id": 111222333,
        "student_full_name": "Глеб Кушедов",
        "mentor_full_name": "Слава Леонтьев",
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

    report_soft_data = {
        "ticket_id": 600101,
        "student_id": 111222333,
        "student_full_name": "Иван Тапорыжкин",
        "mentor_full_name": "Слава Леонтьев",
        "stream_name": "Python 0.0",
        "task_name": "Домашка тестовая 1.1",
        "skills": {
            "skill_1": 1,
            "skill_2": 1,
            "skill_3": 2,
            "skill_4": 0
        }
    }

    # /report
    def test_criteria_report(self):
        headers = {"Content-Type": "application/json"}
        response = requests.post(SERVER_URL + "report", data=json.dumps(self.report_criteria_data), headers=headers)
        assert response.status_code == 201, "Status code is not 201"

    # /report-soft-skills
    def test_soft_skills_report(self):
        headers = {"Content-Type": "application/json"}
        response = requests.post(SERVER_URL + "report-soft-skills", data=json.dumps(self.report_soft_data),
                                 headers=headers)
        assert response.status_code == 201, "Status code is not 201"


class TestWikiRequests:

    def test_requests_to_wiki(self):
        response = requests.get(SERVER_URL + "explain/Работает с атрибутами класса./?student_id=1234567")
        assert response.status_code == 200, "Status code is not 200"
