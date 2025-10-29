from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base_model import Base
from src.schemas import QuestionSchema

if TYPE_CHECKING:
    from src.db.models.answer_model import AnswerOrm


class QuestionOrm(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(10_000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # связи
    answers: Mapped[list["AnswerOrm"]] = relationship(
        back_populates="question",
        passive_deletes=True,
    )

    def to_read_model(self) -> QuestionSchema:
        return QuestionSchema(
            id=self.id,
            text=self.text,
            created_at=self.created_at,
            answers=[answer.to_read_model() for answer in self.answers],
        )
