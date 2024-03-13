from pydantic import BaseModel


class ChecklistReport(BaseModel):
    checklist_data: dict
    ticket_id: int
    student_full_name: str
    mentor_full_name: str
    stream_name: str
