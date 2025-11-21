from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.answers_rep import AnswersRepository
from src.db.repositories.questions_rep import QuestionsRepository


class IUnitOfWork(ABC):
    answers_repo: AnswersRepository
    questions_repo: QuestionsRepository

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork": ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb) -> bool: ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class UnitOfWork:
    def __init__(self, async_session_maker):
        self.session_factory = async_session_maker
        self.session: AsyncSession | None = None

        self.answers_repo: AnswersRepository | None = None
        self.questions_repo: QuestionsRepository | None = None

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self.session_factory()
        # создаём репозитории на этой сессии
        self.answers_repo = AnswersRepository(self.session)
        self.questions_repo = QuestionsRepository(self.session)

        return self

    async def __aexit__(self, exc_type: type | None, exc, tb) -> bool | None:
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
