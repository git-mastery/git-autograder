from git_autograder.answers.answers_record import GitAutograderAnswersRecord
from git_autograder.answers.rules.answer_rule import AnswerRule


class NotEmptyRule(AnswerRule):
    EMPTY = "Answer for {question} is empty."

    def apply(self, answer: GitAutograderAnswersRecord) -> None:
        if answer.answer.strip() == "":
            raise Exception(self.EMPTY.format(question=answer.question))
