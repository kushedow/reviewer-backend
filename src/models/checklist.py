from enum import Enum

from pydantic import BaseModel, Field


class ChecklistStatusEnum(str, Enum):
    OK = "OK"
    ERROR = "ERROR"
    LOADING = "LOADING"


checklist_example = [
    {
        "title": "Функциональный код разбит на модули",
        "5": "Функциональный код разбит на модули: модуль для взаимодействия с API, модуль для взаимодействия "
             "с файлами, модуль для взаимодействия с вакансиями ",
        "3": "Функциональный код не разбит на модули",
        "group": "Общие критерии для проекта",
        "homework": "",
        "skill": "",
        "hint": "Тут важно проверить что не все в одном файле лежит, а разбито логически по модулям"
    }
]


class Checklist(BaseModel):
    lesson: str = Field(description="4.2 Циклы. Часть 2", examples=["Ты молодец, ты выполнил задание"])
    sheet_id: str = Field(description="ID дока с критериями", examples=["1OwCJ8-Jt1WbNxwg-ik_4zjD5z6pQYV1yPUTryafn0bU"])

    profession: str = Field(default="", description="Профессия, к которой чеклист", examples=["PD"])
    body: list[dict] = Field(default=[], description="Тело чеклиста", examples=[checklist_example])
    status: ChecklistStatusEnum = Field(default=ChecklistStatusEnum.LOADING, description="Статус чеклиста",
                                        examples=["OK", "ERROR", "LOADING"])

    motivation: str = Field(default="", description="Мотивашка после выполнения",
                            examples=["Ты молодец, ты выполнил задание"])
    softcheck: bool = Field(default=False, description="Софтчек?", examples=[True, False])
    is_ready: bool = Field(default=True, description="Активен ли чеклист?", examples=[True, False])
