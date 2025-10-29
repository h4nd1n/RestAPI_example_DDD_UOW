from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
async def test_create_answer_201(client, answers_repo, valid_answer_payload):
    async def _add_one(data: dict) -> int:
        # контролируем, что сервис добавляет question_id в dict
        assert "question_id" in data
        assert data["user_id"] == valid_answer_payload["user_id"]
        assert data["text"] == valid_answer_payload["text"]
        return 555  # сервис/роутер возвращают int

    answers_repo._add_one = _add_one

    question_id = 123
    r = await client.post(
        f"/questions/{question_id}/answers", json=valid_answer_payload
    )
    assert r.status_code == 201
    assert r.json() == 555


@pytest.mark.asyncio
async def test_create_answer_404_on_integrity_error(
    client, answers_repo, valid_answer_payload
):
    async def _add_one(data: dict):
        # имитация внешнего ключа на несуществующий вопрос
        raise IntegrityError("insert", "params", "fk violation")

    answers_repo._add_one = _add_one

    r = await client.post("/questions/999/answers", json=valid_answer_payload)
    assert r.status_code == 404
    assert r.json()["detail"] == "Question not found"


@pytest.mark.asyncio
async def test_create_answer_500_on_unexpected(
    client, answers_repo, valid_answer_payload
):
    async def _boom(data: dict):
        raise RuntimeError("unexpected")

    answers_repo._add_one = _boom

    r = await client.post("/questions/1/answers", json=valid_answer_payload)
    assert r.status_code == 500
    assert r.json()["detail"] == "Internal Server Error"


@pytest.mark.asyncio
async def test_get_answer_200(client, answers_repo):
    async def _find_one(answer_id: int):
        return {
            "id": answer_id,
            "question_id": 1,
            "user_id": "e2b50b32-76ae-42f9-a012-4e5ae315645b",
            "text": "ok",
            "created_at": datetime.now(UTC),
        }

    answers_repo._find_one = _find_one

    r = await client.get("/answers/7")
    assert r.status_code == 200
    assert r.json()["id"] == 7


@pytest.mark.asyncio
async def test_get_answer_404(client, answers_repo):
    async def _find_one(answer_id: int):
        return None

    answers_repo._find_one = _find_one

    r = await client.get("/answers/777")
    assert r.status_code == 404
    assert r.json()["detail"] == "Answer not found"


@pytest.mark.asyncio
async def test_get_answer_500(client, answers_repo):
    async def _boom(answer_id: int):
        raise RuntimeError("db fail")

    answers_repo._find_one = _boom

    r = await client.get("/answers/1")
    assert r.status_code == 500
    assert r.json()["detail"] == "Internal Server Error"


@pytest.mark.asyncio
async def test_delete_answer_204(client, answers_repo):
    async def _del(answer_id: int):
        return True

    answers_repo._del_one = _del

    r = await client.delete("/answers/5")
    assert r.status_code == 204
    assert r.text == ""


@pytest.mark.asyncio
async def test_delete_answer_404(client, answers_repo):
    async def _del(answer_id: int):
        return False

    answers_repo._del_one = _del

    r = await client.delete("/answers/5")
    assert r.status_code == 404
    assert r.json()["detail"] == "Answer not found"


@pytest.mark.asyncio
async def test_delete_answer_500_on_exception(client, answers_repo):
    async def _boom(answer_id: int):
        raise RuntimeError("db fail")

    answers_repo._del_one = _boom

    r = await client.delete("/answers/5")
    assert r.status_code == 500
    assert r.json()["detail"] == "Internal Server Error"
