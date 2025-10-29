from src.schemas import QuestionSchema
from src.schemas.question_schema import QuestionCreateSchema
from src.utils.repository import AbstractRepository


class QuestionsService:
    def __init__(self, questions_repo: AbstractRepository):
        self.questions_repo = questions_repo

    async def add_question(self, question: QuestionCreateSchema) -> int:
        question_dict = question.model_dump()
        question_id = await self.questions_repo.add_one(question_dict)
        return question_id

    async def delete_question(self, question_id) -> bool:
        question_id = await self.questions_repo.del_one(question_id)
        return bool(question_id)

    async def get_question(self, question_id: int) -> QuestionSchema | None:
        return await self.questions_repo.find_one(question_id)

    async def get_questions(self) -> list[QuestionSchema | None]:
        questions = await self.questions_repo.find_all()
        return questions
