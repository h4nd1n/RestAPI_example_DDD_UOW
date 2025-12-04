import pytest

from src.core.domain_exceptions import (
    AnswerNotFoundException,
    QuestionNotFoundException,
)
from src.db.db_exceptions import ForeignKeyViolation
from src.schemas.answers_schema import AnswerCreateSchema
from src.schemas.question_schema import QuestionCreateSchema


@pytest.mark.asyncio
async def test_answers_service_add_answer_ok(answers_service, answers_repo):
    async def _add_one(data: dict):
        assert data["question_id"] == 1
        assert data["text"] == "t"
        return 42

    answers_repo._add_one = _add_one

    answer_id = await answers_service.add_answer(
        AnswerCreateSchema(user_id="u", text="t"), question_id=1
    )
    assert answer_id == 42


@pytest.mark.asyncio
async def test_answers_service_add_answer_maps_foreign_key_to_question_not_found(
    answers_service, answers_repo
):
    async def _add_one(_):
        raise ForeignKeyViolation()

    answers_repo._add_one = _add_one

    with pytest.raises(QuestionNotFoundException):
        await answers_service.add_answer(
            AnswerCreateSchema(user_id="u", text="t"), question_id=999
        )


@pytest.mark.asyncio
async def test_answers_service_delete_not_found(answers_service, answers_repo):
    async def _del_one(_):
        return False

    answers_repo._del_one = _del_one

    with pytest.raises(AnswerNotFoundException):
        await answers_service.delete_answer(1)


@pytest.mark.asyncio
async def test_answers_service_get_not_found(answers_service, answers_repo):
    async def _find_one(_):
        return None

    answers_repo._find_one = _find_one

    with pytest.raises(AnswerNotFoundException):
        await answers_service.get_answer(1)


# QuestionsService


@pytest.mark.asyncio
async def test_questions_service_add_question_ok(questions_service, questions_repo):
    async def _add_one(data: dict):
        assert data["text"] == "hello"
        return 7

    questions_repo._add_one = _add_one

    question_id = await questions_service.add_question(
        QuestionCreateSchema(text="hello")
    )
    assert question_id == 7


@pytest.mark.asyncio
async def test_questions_service_delete_not_found(questions_service, questions_repo):
    async def _del_one(_):
        return False

    questions_repo._del_one = _del_one

    with pytest.raises(QuestionNotFoundException):
        await questions_service.delete_question(1)


@pytest.mark.asyncio
async def test_questions_service_get_not_found(questions_service, questions_repo):
    async def _find_one(_):
        return None

    questions_repo._find_one = _find_one

    with pytest.raises(QuestionNotFoundException):
        await questions_service.get_question(1)


@pytest.mark.asyncio
async def test_questions_service_get_list(questions_service, questions_repo):
    async def _find_all():
        return [{"id": 1, "text": "a"}, {"id": 2, "text": "b"}]

    questions_repo._find_all = _find_all

    questions = await questions_service.get_questions()
    assert [q["id"] for q in questions] == [1, 2]
