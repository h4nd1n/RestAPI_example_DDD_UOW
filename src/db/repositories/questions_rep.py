from src.db.models.question_model import QuestionOrm
from src.utils.repository import SqlAlchemyQuestionsRepository


class QuestionsRepository(SqlAlchemyQuestionsRepository):
    model = QuestionOrm
