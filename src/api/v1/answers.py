import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.api.v1.deps import get_answers_service
from src.schemas.answers_schema import AnswerCreateSchema, AnswerSchema
from src.services.answers_service import AnswersService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["answers"])


@router.post(
    "/questions/{question_id}/answers",
    status_code=status.HTTP_201_CREATED,
    summary="Создать ответ на вопрос",
    description="Создаёт новый ответ на существующий вопрос и возвращает его идентификатор.",
    response_model=int,
    responses={
        status.HTTP_201_CREATED: {"description": "Answer created"},
        status.HTTP_404_NOT_FOUND: {"description": "Question not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)
async def create_answer_endpoint(
    question_id: int,
    answer: AnswerCreateSchema,
    answers_service: Annotated[AnswersService, Depends(get_answers_service)],
):
    return await answers_service.add_answer(answer=answer, question_id=question_id)


@router.get(
    "/answers/{answer_id}",
    status_code=status.HTTP_200_OK,
    summary="Получить ответ",
    description="Возвращает ответ по идентификатору.",
    response_model=AnswerSchema,
    responses={
        status.HTTP_200_OK: {"description": "Answer found"},
        status.HTTP_404_NOT_FOUND: {"description": "Answer not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)
async def get_answer_endpoint(
    answer_id: int,
    answers_service: Annotated[AnswersService, Depends(get_answers_service)],
):
    return await answers_service.get_answer(answer_id=answer_id)


@router.delete(
    "/answers/{answer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить ответ",
    description="Удаляет ответ по идентификатору.",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Answer deleted"},
        status.HTTP_404_NOT_FOUND: {"description": "Answer not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)
async def delete_answer_endpoint(
    answer_id: int,
    answers_service: Annotated[AnswersService, Depends(get_answers_service)],
):
    return await answers_service.delete_answer(answer_id=answer_id)
