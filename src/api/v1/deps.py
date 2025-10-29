from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.answers_rep import AnswersRepository
from src.db.repositories.questions_rep import QuestionsRepository
from src.services.answers_service import AnswersService
from src.services.questions_service import QuestionsService
from src.utils.unitofwork import UnitOfWork


async def get_session(request: Request) -> AsyncSession:
    session_maker = request.app.state.db.session_maker
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_answers_service(session: Annotated[AsyncSession, Depends(get_session)]):
    return AnswersService(AnswersRepository(session))


def get_questions_service(session: Annotated[AsyncSession, Depends(get_session)]):
    return QuestionsService(QuestionsRepository(session))


def get_unit_of_work(request: Request):
    return UnitOfWork(request.app.state.db.session_maker)
