import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.api import health as health_router_module
from src.api.exception_handlers import setup_exception_handlers
from src.api.v1 import (
    answers as answers_router_module,
    deps,
    questions as questions_router_module,
)
from src.services.answers_service import AnswersService
from src.services.questions_service import QuestionsService
from src.utils.repository import AbstractRepository

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


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(health_router_module.router, prefix="/health")
    app.include_router(questions_router_module.router)
    app.include_router(answers_router_module.router)
    setup_exception_handlers(app)
    return app


@pytest.fixture
def answers_repo():
    return FakeRepo()


@pytest.fixture
def questions_repo():
    return FakeRepo()


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
def override_services(app, answers_repo, questions_repo):
    class TestUnitOfWork:
        def __init__(self, answers_repo, questions_repo):
            self.answers_repo = answers_repo
            self.questions_repo = questions_repo

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False  # не подавляем исключения

        async def commit(self):
            pass

        async def rollback(self):
            pass

    def uow_factory() -> TestUnitOfWork:
        return TestUnitOfWork(answers_repo, questions_repo)

    def _uow_override():
        return uow_factory

    async def _answers_service_override():
        return AnswersService(uow_factory=uow_factory)

    async def _questions_service_override():
        return QuestionsService(uow_factory=uow_factory)

    app.dependency_overrides[deps.get_uow_factory] = _uow_override
    app.dependency_overrides[deps.get_answers_service] = _answers_service_override
    app.dependency_overrides[deps.get_questions_service] = _questions_service_override
    yield
    app.dependency_overrides.clear()


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
