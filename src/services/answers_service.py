from src.schemas import AnswerSchema
from src.schemas.answers_schema import AnswerCreateSchema
from src.utils.repository import AbstractRepository
from src.utils.unitofwork import UnitOfWork


class AnswersService:
    def __init__(self, answers_repo: AbstractRepository):
        self.answers_repo = answers_repo

    async def add_answer(
        self, answer: AnswerCreateSchema, question_id: int, uow: UnitOfWork
    ) -> int:
        answer_dict = answer.model_dump()
        async with uow:
            answer_dict["question_id"] = question_id
            answer_id = await uow.answers_repo.add_one(data=answer_dict)
            return answer_id

    async def delete_answer(self, answer_id, uow: UnitOfWork) -> bool:
        async with uow:
            answer_id = await uow.answers_repo.del_one(answer_id)
            return bool(answer_id)

    async def get_answer(self, answer_id) -> AnswerSchema | None:
        return await self.answers_repo.find_one(answer_id)

    async def get_answers(self) -> list[AnswerSchema]:
        answers = await self.answers_repo.find_all()
        return answers
