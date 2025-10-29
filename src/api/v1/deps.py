from fastapi import Request

from src.db.repositories.answers_rep import AnswersRepository
from src.db.repositories.questions_rep import QuestionsRepository
from src.services.answers_service import AnswersService
from src.services.questions_service import QuestionsService


def get_answers_service(request: Request):
    return AnswersService(AnswersRepository(request.app.state.db.session_maker))


def get_questions_service(request: Request):
    return QuestionsService(QuestionsRepository(request.app.state.db.session_maker))
