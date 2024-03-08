from pydantic import BaseModel


class SkillRecord(BaseModel):
    ticket_id: int
    skill: str
    grade: int
