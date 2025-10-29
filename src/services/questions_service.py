from src.schemas import QuestionSchema
from src.schemas.question_schema import QuestionCreateSchema
from src.utils.repository import AbstractRepository
from src.utils.unitofwork import UnitOfWork


class QuestionsService:
    def __init__(self, questions_repo: AbstractRepository):
        self.questions_repo = questions_repo

    async def add_question(
        self, question: QuestionCreateSchema, uow: UnitOfWork
    ) -> int:
        async with uow:
            question_dict = question.model_dump()
            question_id = await uow.questions_repo.add_one(question_dict)
            return question_id

    async def delete_question(self, question_id, uow: UnitOfWork) -> bool:
        async with uow:
            question_id = await uow.questions_repo.del_one(question_id)
            return bool(question_id)

    async def get_question(self, question_id: int) -> QuestionSchema | None:
        return await self.questions_repo.find_one(question_id)

    async def get_questions(self) -> list[QuestionSchema | None]:
        questions = await self.questions_repo.find_all()
        return questions
