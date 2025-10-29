from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.schemas import AnswerSchema


class QuestionBaseSchema(BaseModel):
    text: str = Field(min_length=1, max_length=10_000)


class QuestionCreateSchema(QuestionBaseSchema):
    pass


class QuestionSchema(QuestionBaseSchema):
    id: int
    created_at: datetime
    answers: list[AnswerSchema]

    model_config = ConfigDict(from_attributes=True)
