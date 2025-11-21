from collections.abc import Callable

from src.core.domain_exceptions import QuestionNotFoundException
from src.schemas import QuestionSchema
from src.schemas.question_schema import QuestionCreateSchema
from src.utils.unitofwork import UnitOfWork


class QuestionsService:
    def __init__(self, uow_factory: Callable[[], UnitOfWork]):
        self._uow_factory = uow_factory

    async def add_question(self, question: QuestionCreateSchema) -> int:
        async with self._uow_factory() as uow:
            question_dict = question.model_dump()
            question_id = await uow.questions_repo.add_one(question_dict)
            return question_id

    async def delete_question(self, question_id) -> bool:
        async with self._uow_factory() as uow:
            deleted = await uow.questions_repo.del_one(question_id)
            if not deleted:
                raise QuestionNotFoundException()
            return deleted

    async def get_question(self, question_id: int) -> QuestionSchema | None:
        async with self._uow_factory() as uow:
            question = await uow.questions_repo.find_one(question_id)
            if not question:
                raise QuestionNotFoundException()
            return question

    async def get_questions(self) -> list[QuestionSchema | None]:
        async with self._uow_factory() as uow:
            questions = await uow.questions_repo.find_all()
            return questions
