import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

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
    try:
        return await questions_service.get_questions()
    except Exception:
        logger.exception("Database error", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from None


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_question_endpoint(
    question: QuestionCreateSchema,
    questions_service: Annotated[QuestionsService, Depends(get_questions_service)],
):
    try:
        return await questions_service.add_question(question)
    except Exception as e:
        logger.exception(f"Unexpected error {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from None


@router.get(
    "/{question_id}",
    status_code=status.HTTP_200_OK,
)
async def get_question_with_answers_endpoint(
    question_id: int,
    questions_service: Annotated[QuestionsService, Depends(get_questions_service)],
):
    try:
        question = await questions_service.get_question(question_id)
    except Exception as e:
        logger.exception(f"Unexpected error {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from None
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question_endpoint(
    question_id: int,
    questions_service: Annotated[QuestionsService, Depends(get_questions_service)],
):
    try:
        deleted = await questions_service.delete_question(question_id)
    except Exception as e:
        logger.exception(f"Unexpected error {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from None
    if not deleted:
        # Ничего не удалено — вопрос не найден
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        ) from None
    return None
