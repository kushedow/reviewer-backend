from datetime import datetime

from pydantic import BaseModel, Field

class RateRequest(BaseModel):

    """Модель оценки вики-статей """
    student_id: int = Field(default=0, examples=[111222333])
    slug: str = Field(default="", examples=["testovoe-nazvanie-statii"])
    personalized: bool = Field(default=False)
    # date: datetime = Field(default_factory=datetime.utcnow)

