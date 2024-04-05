from pydantic import BaseModel, Field


class ChecklistRequest(BaseModel):
    ticket_id: int
    student_full_name: str
    mentor_full_name: str
    stream_name: str
    task_name: str = Field(default=None)
    sheet_id: str = Field(default=None)
