import logging

from fastapi import APIRouter, FastAPI
from starlette import status
from starlette.responses import JSONResponse

from src.core.domain_exceptions import (
    AnswerNotFoundException,
    QuestionNotFoundException,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["exception"])


async def global_exception_handler(request, exc):
    logger.exception(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


async def question_not_found_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Question not found"}
    )


async def answer_not_found_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Answer not found"}
    )


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AnswerNotFoundException, answer_not_found_handler)
    app.add_exception_handler(QuestionNotFoundException, question_not_found_handler)
    app.add_exception_handler(Exception, global_exception_handler)
