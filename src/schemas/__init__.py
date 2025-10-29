from src.schemas.answers_schema import AnswerSchema
from src.schemas.question_schema import QuestionSchema

QuestionSchema.model_rebuild()
AnswerSchema.model_rebuild()
