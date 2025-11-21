import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.api.v1.deps import get_answers_service
from src.schemas.answers_schema import AnswerCreateSchema
from src.services.answers_service import AnswersService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["answers"])


@router.post("/questions/{question_id}/answers", status_code=status.HTTP_201_CREATED)
async def create_answer_endpoint(
    question_id: int,
    answer: AnswerCreateSchema,
    answers_service: Annotated[AnswersService, Depends(get_answers_service)],
):
    return await answers_service.add_answer(answer=answer, question_id=question_id)


@router.get("/answers/{answer_id}")
async def get_answer_endpoint(
    answer_id: int,
    answers_service: Annotated[AnswersService, Depends(get_answers_service)],
):
    return await answers_service.get_answer(answer_id=answer_id)


@router.delete("/answers/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer_endpoint(
    answer_id: int,
    answers_service: Annotated[AnswersService, Depends(get_answers_service)],
):
    return await answers_service.delete_answer(answer_id=answer_id)
