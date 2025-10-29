from abc import ABC, abstractmethod

from src.db.repositories.answers_rep import AnswersRepository
from src.db.repositories.questions_rep import QuestionsRepository


class IUnitOfWork(ABC):
    answers_repo: type[AnswersRepository]
    questions_repo: type[QuestionsRepository]

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, *args): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class UnitOfWork:
    def __init__(self, async_session_maker):
        self.session_factory = async_session_maker

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self.session_factory()

        self.answers_repo = AnswersRepository(self.session)
        self.questions_repo = QuestionsRepository(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if exc:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()
        # не подавляем исключения
        return False

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
