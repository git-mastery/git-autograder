from git_autograder.answers.rules import AnswerRule
from git_autograder.answers import GitAutograderAnswersRecord


class ContainsValueRule(AnswerRule):
    def __init__(self, value: str, is_case_sensitive: bool = False) -> None:
        self.value = value
        self.is_case_sensitive = is_case_sensitive

    def apply(self, answer: GitAutograderAnswersRecord) -> None:
        expected = self.value.lower() if self.is_case_sensitive else self.value
        given = answer.answer.lower() if self.is_case_sensitive else answer.answer
        if given not in expected:
            raise Exception(
                f"Answer for {answer.question} does not contain the right answer."
            )
