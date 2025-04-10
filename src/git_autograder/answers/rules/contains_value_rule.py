from git_autograder.answers.answers_record import GitAutograderAnswersRecord
from git_autograder.answers.rules.answer_rule import AnswerRule


class ContainsValueRule(AnswerRule):
    MISSING_ANSWER = "Answer for {question} does not contain the right answer."

    def __init__(self, value: str, is_case_sensitive: bool = False) -> None:
        self.value = value
        self.is_case_sensitive = is_case_sensitive

    def apply(self, answer: GitAutograderAnswersRecord) -> None:
        expected = self.value.lower() if self.is_case_sensitive else self.value
        given = answer.answer.lower() if self.is_case_sensitive else answer.answer
        if given not in expected:
            raise Exception(self.MISSING_ANSWER.format(question=answer.question))
