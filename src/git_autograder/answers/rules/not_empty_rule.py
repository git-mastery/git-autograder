from git_autograder.answers.answers_record import GitAutograderAnswersRecord
from git_autograder.answers.rules.answer_rule import AnswerRule


class NotEmptyRule(AnswerRule):
    def apply(self, answer: GitAutograderAnswersRecord) -> None:
        if answer.answer.strip() != "":
            raise Exception(f"Answer for {answer.question} is empty.")
