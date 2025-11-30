import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.api.v1.deps import get_questions_service
from src.schemas.question_schema import QuestionCreateSchema, QuestionSchema
from src.services.questions_service import QuestionsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Список вопросов",
    description="Возвращает список всех вопросов с вложенными ответами.",
    response_model=list[QuestionSchema],
    responses={
        status.HTTP_200_OK: {"description": "Questions list"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)
async def get_questions_endpoint(
    questions_service: Annotated[QuestionsService, Depends(get_questions_service)],
):
    return await questions_service.get_questions()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Создать вопрос",
    description="Создаёт новый вопрос и возвращает его идентификатор.",
    response_model=int,
    responses={
        status.HTTP_201_CREATED: {"description": "Question created"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)
async def create_question_endpoint(
    question: QuestionCreateSchema,
    questions_service: Annotated[QuestionsService, Depends(get_questions_service)],
):
    return await questions_service.add_question(question)


@router.get(
    "/{question_id}",
    status_code=status.HTTP_200_OK,
    summary="Получить вопрос",
    description="Возвращает вопрос по идентификатору с вложенными ответами.",
    response_model=QuestionSchema,
    responses={
        status.HTTP_200_OK: {"description": "Question found"},
        status.HTTP_404_NOT_FOUND: {"description": "Question not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)
async def get_question_with_answers_endpoint(
    question_id: int,
    questions_service: Annotated[QuestionsService, Depends(get_questions_service)],
):
    return await questions_service.get_question(question_id)


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить вопрос",
    description="Удаляет вопрос по идентификатору.",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Question deleted"},
        status.HTTP_404_NOT_FOUND: {"description": "Question not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)
async def delete_question_endpoint(
    question_id: int,
    questions_service: Annotated[QuestionsService, Depends(get_questions_service)],
):
    return await questions_service.delete_question(question_id)
