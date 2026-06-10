from pydantic import BaseModel


class DigitalBuddyQuestion(BaseModel):
    employee_id: int
    question: str
    language: str | None = None


class DigitalBuddyAnswer(BaseModel):
    answer: str
    source: str | None = None
    section: str | None = None
    document_code: str | None = None
    sentiment: str | None = None
    language: str | None = None
    mode: str | None = None
