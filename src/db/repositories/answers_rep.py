from src.db.models.answer_model import AnswerOrm
from src.utils.repository import SqlAlchemyRepository


class AnswersRepository(SqlAlchemyRepository):
    model = AnswerOrm
