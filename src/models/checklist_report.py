from pydantic import BaseModel, Field


class ChecklistReport(BaseModel):
    checklist_data: dict
    ticket_id: int
    student_id: int = Field(default=0)
    student_full_name: str
    mentor_full_name: str
    stream_name: str
    task_name: str = Field(default='')

