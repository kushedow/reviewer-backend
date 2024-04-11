from pydantic import BaseModel, Field


class AIRequest(BaseModel):

    # Обязательные
    ticket_id: int = Field(description="ID проверяемого тикета")
    student_full_name: str = Field(description="Имя ученика, чью работу мы проверяем")
    mentor_full_name: str = Field(description="Имя наставника, на которого назначен тикет")
    stream_name: str = Field(description="Название потока, на котором ученик")

    # Опциональные
    q: str = Field(default='', description="Сырой текст запроса")  # DEPRECATED
    prompt_name: str = Field(default='', description="Название промпта из таблички с промптами")
    feedback_body: str = Field(default='', description="Составленная ОС для ученика")
    task_name: str = Field(default='', description="Название задания, которое мы проверяем")
