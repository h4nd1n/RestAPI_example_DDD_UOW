from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base_model import Base
from src.schemas import AnswerSchema

if TYPE_CHECKING:
    from src.db.models.question_model import QuestionOrm


class AnswerOrm(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[str] = mapped_column(String(200), nullable=False)
    text: Mapped[str] = mapped_column(String(10_000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # связи
    question: Mapped["QuestionOrm"] = relationship(back_populates="answers")

    def to_read_model(self) -> AnswerSchema:
        return AnswerSchema(
            user_id=self.user_id,
            text=self.text,
            id=self.id,
            question_id=self.question_id,
            created_at=self.created_at,
        )
