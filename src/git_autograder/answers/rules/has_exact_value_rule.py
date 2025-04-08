from git_autograder.answers.answers_record import GitAutograderAnswersRecord
from git_autograder.answers.rules.answer_rule import AnswerRule


class HasExactValueRule(AnswerRule):
    def __init__(self, value: str, is_case_sensitive: bool = False) -> None:
        super().__init__()
        self.value = value
        self.is_case_sensitive = is_case_sensitive

    def apply(self, answer: GitAutograderAnswersRecord) -> None:
        expected = self.value.lower() if self.is_case_sensitive else self.value
        given = answer.answer.lower() if self.is_case_sensitive else answer.answer
        if given != expected:
            raise Exception(f"Answer for {answer.question} is not right.")
