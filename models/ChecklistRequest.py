from pydantic import BaseModel


class ChecklistRequest(BaseModel):
    sheet_id: str
    ticket_id: int
    student_full_name: str
    mentor_full_name: str
    stream_name: str
