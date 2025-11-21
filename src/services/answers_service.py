from collections.abc import Callable

from src.core.domain_exceptions import (
    AnswerNotFoundException,
    QuestionNotFoundException,
)
from src.db.db_exceptions import ForeignKeyViolation
from src.schemas import AnswerSchema
from src.schemas.answers_schema import AnswerCreateSchema
from src.utils.unitofwork import UnitOfWork


class AnswersService:
    def __init__(self, uow_factory: Callable[[], UnitOfWork]):
        self._uow_factory = uow_factory

    async def add_answer(self, answer: AnswerCreateSchema, question_id: int) -> int:
        try:
            answer_dict = answer.model_dump()
            async with self._uow_factory() as uow:
                answer_dict["question_id"] = question_id
                answer_id = await uow.answers_repo.add_one(data=answer_dict)
                return answer_id
        except ForeignKeyViolation as e:
            raise QuestionNotFoundException() from e

    async def delete_answer(self, answer_id: int) -> bool:
        async with self._uow_factory() as uow:
            deleted = await uow.answers_repo.del_one(answer_id)
            if not deleted:
                raise AnswerNotFoundException()
            return deleted

    async def get_answer(self, answer_id) -> AnswerSchema:
        async with self._uow_factory() as uow:
            answer = await uow.answers_repo.find_one(answer_id)
            if answer is None:
                raise AnswerNotFoundException()
            return answer

    async def get_answers(self) -> list[AnswerSchema]:
        async with self._uow_factory() as uow:
            return await uow.answers_repo.find_all()
