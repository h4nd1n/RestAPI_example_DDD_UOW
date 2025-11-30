import pytest

from src.core.domain_exceptions import (
    AnswerNotFoundException,
    QuestionNotFoundException,
)
from src.db.db_exceptions import ForeignKeyViolation
from src.schemas.answers_schema import AnswerCreateSchema
from src.schemas.question_schema import QuestionCreateSchema
from src.services.answers_service import AnswersService
from src.services.questions_service import QuestionsService


class _FakeRepo:
    def __init__(self):
        self._add_one = None
        self._del_one = None
        self._find_one = None
        self._find_all = None

    async def add_one(self, data: dict):
        return await self._add_one(data)

    async def del_one(self, object_id: int):
        return await self._del_one(object_id)

    async def find_one(self, object_id: int):
        return await self._find_one(object_id)

    async def find_all(self):
        return await self._find_all()


class _FakeUow:
    def __init__(
        self,
        answers_repo: _FakeRepo | None = None,
        questions_repo: _FakeRepo | None = None,
    ):
        self.answers_repo = answers_repo or _FakeRepo()
        self.questions_repo = questions_repo or _FakeRepo()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def commit(self):
        pass

    async def rollback(self):
        pass


def _uow_factory(uow: _FakeUow):
    def factory():
        return uow

    return factory


# AnswersService


@pytest.mark.asyncio
async def test_answers_service_add_answer_ok():
    repo = _FakeRepo()

    async def _add_one(data: dict):
        assert data["question_id"] == 1
        assert data["text"] == "t"
        return 42

    repo._add_one = _add_one
    service = AnswersService(uow_factory=_uow_factory(_FakeUow(answers_repo=repo)))

    answer_id = await service.add_answer(
        AnswerCreateSchema(user_id="u", text="t"), question_id=1
    )
    assert answer_id == 42


@pytest.mark.asyncio
async def test_answers_service_add_answer_maps_foreign_key_to_question_not_found():
    repo = _FakeRepo()

    async def _add_one(_):
        raise ForeignKeyViolation()

    repo._add_one = _add_one
    service = AnswersService(uow_factory=_uow_factory(_FakeUow(answers_repo=repo)))

    with pytest.raises(QuestionNotFoundException):
        await service.add_answer(
            AnswerCreateSchema(user_id="u", text="t"), question_id=999
        )


@pytest.mark.asyncio
async def test_answers_service_delete_not_found():
    repo = _FakeRepo()

    async def _del_one(_):
        return False

    repo._del_one = _del_one
    service = AnswersService(uow_factory=_uow_factory(_FakeUow(answers_repo=repo)))

    with pytest.raises(AnswerNotFoundException):
        await service.delete_answer(1)


@pytest.mark.asyncio
async def test_answers_service_get_not_found():
    repo = _FakeRepo()

    async def _find_one(_):
        return None

    repo._find_one = _find_one
    service = AnswersService(uow_factory=_uow_factory(_FakeUow(answers_repo=repo)))

    with pytest.raises(AnswerNotFoundException):
        await service.get_answer(1)


# QuestionsService


@pytest.mark.asyncio
async def test_questions_service_add_question_ok():
    repo = _FakeRepo()

    async def _add_one(data: dict):
        assert data["text"] == "hello"
        return 7

    repo._add_one = _add_one
    service = QuestionsService(uow_factory=_uow_factory(_FakeUow(questions_repo=repo)))

    question_id = await service.add_question(QuestionCreateSchema(text="hello"))
    assert question_id == 7


@pytest.mark.asyncio
async def test_questions_service_delete_not_found():
    repo = _FakeRepo()

    async def _del_one(_):
        return False

    repo._del_one = _del_one
    service = QuestionsService(uow_factory=_uow_factory(_FakeUow(questions_repo=repo)))

    with pytest.raises(QuestionNotFoundException):
        await service.delete_question(1)


@pytest.mark.asyncio
async def test_questions_service_get_not_found():
    repo = _FakeRepo()

    async def _find_one(_):
        return None

    repo._find_one = _find_one
    service = QuestionsService(uow_factory=_uow_factory(_FakeUow(questions_repo=repo)))

    with pytest.raises(QuestionNotFoundException):
        await service.get_question(1)


@pytest.mark.asyncio
async def test_questions_service_get_list():
    repo = _FakeRepo()

    async def _find_all():
        return [{"id": 1, "text": "a"}, {"id": 2, "text": "b"}]

    repo._find_all = _find_all
    service = QuestionsService(uow_factory=_uow_factory(_FakeUow(questions_repo=repo)))

    questions = await service.get_questions()
    assert [q["id"] for q in questions] == [1, 2]
