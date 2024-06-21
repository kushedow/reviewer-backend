from pydantic import BaseModel, Field


class ChecklistRequest(BaseModel):
    ticket_id: int = Field(examples=[111_111])
    student_full_name: str= Field(examples=["Глеб Кушедов"])
    mentor_full_name: str= Field(examples=["Слава Леонтьев"])
    stream_name: str= Field(examples=["Тестовый поток"])
    task_name: str = Field(default="", examples=["13.1 Введение в ООП"])
    sheet_id: str = Field(default=None, examples=[])
