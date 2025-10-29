from datetime import UTC, datetime

import pytest


@pytest.mark.asyncio
async def test_list_questions_200(client, questions_repo):
    async def _find_all():
        return [
            {"id": 1, "text": "test", "created_at": datetime.now(UTC), "answers": []},
            {"id": 2, "text": "test2", "created_at": datetime.now(UTC), "answers": []},
        ]

    questions_repo._find_all = _find_all

    r = await client.get("/questions")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert {q["id"] for q in body} == {1, 2}


@pytest.mark.asyncio
async def test_list_questions_500(client, questions_repo):
    async def _boom():
        raise RuntimeError("db down")

    questions_repo._find_all = _boom

    r = await client.get("/questions")
    assert r.status_code == 500
    assert r.json()["detail"] == "Internal Server Error"


@pytest.mark.asyncio
async def test_create_question_201(client, questions_repo, valid_question_payload):
    async def _add_one(data: dict) -> int:
        # сервис возвращает int (id)
        assert data["text"] == valid_question_payload["text"]
        return 123

    questions_repo._add_one = _add_one

    r = await client.post("/questions", json=valid_question_payload)
    assert r.status_code == 201
    assert r.json() == 123  # эндпойнт возвращает int, не объект


@pytest.mark.asyncio
async def test_create_question_500(client, questions_repo, valid_question_payload):
    async def _boom(data: dict):
        raise RuntimeError("unexpected")

    questions_repo._add_one = _boom

    r = await client.post("/questions", json=valid_question_payload)
    assert r.status_code == 500
    assert r.json()["detail"] == "Internal Server Error"


@pytest.mark.asyncio
async def test_get_question_with_answers_200(client, questions_repo):
    async def _find_one(question_id: int):
        return {
            "id": question_id,
            "text": "test",
            "created_at": datetime.now(UTC),
            "answers": [],
        }

    questions_repo._find_one = _find_one

    r = await client.get("/questions/42")
    assert r.status_code == 200
    assert r.json()["id"] == 42


@pytest.mark.asyncio
async def test_get_question_with_answers_404(client, questions_repo):
    async def _find_one(question_id: int):
        return None

    questions_repo._find_one = _find_one

    r = await client.get("/questions/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Question not found"


@pytest.mark.asyncio
async def test_get_question_with_answers_500(client, questions_repo):
    async def _boom(question_id: int):
        raise RuntimeError("crash")

    questions_repo._find_one = _boom

    r = await client.get("/questions/1")
    assert r.status_code == 500
    assert r.json()["detail"] == "Internal Server Error"


@pytest.mark.asyncio
async def test_delete_question_204(client, questions_repo):
    async def _del_one(question_id: int):
        return True

    questions_repo._del_one = _del_one

    r = await client.delete("/questions/10")
    assert r.status_code == 204
    assert r.text == ""


@pytest.mark.asyncio
async def test_delete_question_404(client, questions_repo):
    async def _del_one(question_id: int):
        return False

    questions_repo._del_one = _del_one

    r = await client.delete("/questions/10")
    assert r.status_code == 404
    assert r.json()["detail"] == "Question not found"


@pytest.mark.asyncio
async def test_delete_question_500(client, questions_repo):
    async def _boom(question_id: int):
        raise RuntimeError("db error")

    questions_repo._del_one = _boom

    r = await client.delete("/questions/10")
    assert r.status_code == 500
    assert r.json()["detail"] == "Internal Server Error"
