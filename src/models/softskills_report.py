from pydantic import BaseModel, Field


class SoftskillsReport(BaseModel):
    ticket_id: int = Field(title="id тикета", examples=[600101])
    student_id: int = Field(default=0, examples=[111222333])
    student_full_name: str = Field(examples=["Иван Тапорыжкин"])
    mentor_full_name: str = Field(examples=["Слава Леонтьев"])
    stream_name: str = Field(examples=["Python 0.0"])
    task_name: str = Field(default='', examples=["Домашка тестовая 1.1"])

    skills: dict[str, int] = Field(default='', examples=[{"skill_1": 1, "skill_2": 1, "skill_3": 2, "skill_4": 0}])
