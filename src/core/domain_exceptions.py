class QuestionsAnswersBaseException(Exception):
    pass


class QuestionNotFoundException(QuestionsAnswersBaseException):
    pass


class AnswerNotFoundException(QuestionsAnswersBaseException):
    pass
