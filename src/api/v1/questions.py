import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.api.v1.deps import get_questions_service
from src.schemas.question_schema import (
    QuestionCreateSchema,
)
from src.services.questions_service import QuestionsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_questions_endpoint(
    questions_service: Annotated[QuestionsService, Depends(get_questions_service)],
):
    return await questions_service.get_questions()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_question_endpoint(
    question: QuestionCreateSchema,
    questions_service: Annotated[QuestionsService, Depends(get_questions_service)],
):
    return await questions_service.add_question(question)


@router.get(
    "/{question_id}",
    status_code=status.HTTP_200_OK,
)
async def get_question_with_answers_endpoint(
    question_id: int,
    questions_service: Annotated[QuestionsService, Depends(get_questions_service)],
):
    return await questions_service.get_question(question_id)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question_endpoint(
    question_id: int,
    questions_service: Annotated[QuestionsService, Depends(get_questions_service)],
):
    return await questions_service.delete_question(question_id)
