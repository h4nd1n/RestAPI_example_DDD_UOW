from collections.abc import Callable

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.api import api_router
from src.api.exception_handlers import setup_exception_handlers
from src.api.v1 import (
    deps,
)
from src.services.answers_service import AnswersService
from src.services.questions_service import QuestionsService
from src.utils.repository import AbstractRepository
from src.utils.unitofwork import IUnitOfWork

# ===== Фейковые репозитории (минимум, что нужно для тестов) ============


class FakeRepo(AbstractRepository):
    def __init__(self):
        # методы подменяются в самих тестах
        self._add_one = None
        self._del_one = None
        self._find_one = None
        self._find_all = None

    async def add_one(self, data: dict) -> int:
        if self._add_one is None:
            raise NotImplementedError
        return await self._add_one(data)

    async def del_one(self, object_id: int) -> int:
        if self._del_one is None:
            raise NotImplementedError
        return await self._del_one(object_id)

    async def find_one(self, object_id: int):
        if self._find_one is None:
            raise NotImplementedError
        return await self._find_one(object_id)

    async def find_all(self):
        if self._find_all is None:
            raise NotImplementedError
        return await self._find_all()


class FakeUoW:
    def __init__(self, answers_repo, questions_repo):
        self.answers_repo = answers_repo
        self.questions_repo = questions_repo

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def commit(self):
        pass

    async def rollback(self):
        pass


@pytest.fixture
def answers_repo():
    return FakeRepo()


@pytest.fixture
def questions_repo():
    return FakeRepo()


@pytest.fixture
def app(questions_repo, answers_repo):
    app = FastAPI()
    app.include_router(api_router)
    setup_exception_handlers(app)

    return app


@pytest.fixture
def override_services(app, answers_repo, questions_repo):
    def override_uow_factory() -> Callable[[], IUnitOfWork]:
        def _factory() -> IUnitOfWork:
            return FakeUoW(questions_repo=questions_repo, answers_repo=answers_repo)

        return _factory

    app.dependency_overrides[deps.get_uow_factory] = override_uow_factory

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def uow_factory(answers_repo, questions_repo):
    def _factory() -> IUnitOfWork:
        return FakeUoW(
            answers_repo=answers_repo,
            questions_repo=questions_repo,
        )

    return _factory


@pytest.fixture
def answers_service(uow_factory) -> AnswersService:
    return AnswersService(uow_factory=uow_factory)


@pytest.fixture
def questions_service(uow_factory) -> QuestionsService:
    return QuestionsService(uow_factory=uow_factory)


@pytest_asyncio.fixture
async def client(app, override_services):
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


# ===== Валидные payload’ы ===============================================


@pytest.fixture
def valid_question_payload():
    # Минимально валидно для QuestionCreateSchema
    return {"text": "Правда, что музыка меняет восприятие вкуса?"}


@pytest.fixture
def valid_answer_payload():
    # Минимально валидно для AnswerCreateSchema
    return {
        "user_id": "e2b50b32-76ae-42f9-a012-4e5ae315645b",
        "text": "Мне кажется, что да",
    }
