from pydantic import BaseModel


class AIRequest(BaseModel):
    q: str
    ticket_id: int
    student_full_name: str
    mentor_full_name: str
    stream_name: str
