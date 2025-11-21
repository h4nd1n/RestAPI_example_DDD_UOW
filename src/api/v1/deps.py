from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Request

from src.services.answers_service import AnswersService
from src.services.questions_service import QuestionsService
from src.utils.unitofwork import UnitOfWork


def get_uow_factory(request: Request) -> Callable[[], UnitOfWork]:
    session_maker = request.app.state.db.session_maker

    def _factory() -> UnitOfWork:
        return UnitOfWork(session_maker)

    return _factory


def get_answers_service(
    uow_factory: Annotated[Callable[[], UnitOfWork], Depends(get_uow_factory)],
) -> AnswersService:
    return AnswersService(uow_factory=uow_factory)


def get_questions_service(
    uow_factory: Annotated[Callable[[], UnitOfWork], Depends(get_uow_factory)],
) -> QuestionsService:
    return QuestionsService(uow_factory=uow_factory)
