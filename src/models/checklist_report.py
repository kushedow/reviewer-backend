from pydantic import BaseModel, Field

checklist_data = {
        "0": {
            "title": "Решение выложено на GitHub",
            "group": "Работа с git",
            "skill": "Рабочий процесс (git status, add, commit)",
            "criteria": "Решение выложено на GitHub",
            "grade": "5",
            "step": "no-step",
            "note": "no-note",
        },
        "1": {
            "title": "В коммиты не добавлены игнорируемые файлы ",
            "group": "Работа с git",
            "skill": "Рабочий процесс (git status, add, commit)",
            "criteria": "В коммиты не добавлены игнорируемые файлы ",
            "grade": "5",
            "step": "no-step",
            "note": "no-note",
        },
        "2": {
            "title": "В проекте есть .gitignore",
            "group": "Работа с git",
            "skill": "Файл .gitignore",
            "criteria": "В проекте есть .gitignore",
            "grade": "5",
            "step": "no-step",
            "note": "no-note",
        }
}

class ChecklistReport(BaseModel):
    """Модель репорта по чеклисту, который отправляет плагин серверу """
    ticket_id: int = Field(examples=[600111])
    student_id: int = Field(default=0, examples=[111222333])
    student_full_name: str = Field(default='', examples=["Глеб Кушедов"])
    mentor_full_name: str = Field(examples=["Слава Леонтьев"])
    stream_name: str = Field(examples=["Python 01"])
    task_name: str = Field(default='', examples=["Тестовое задание"])
    checklist_data: dict = Field(examples=[checklist_data])

