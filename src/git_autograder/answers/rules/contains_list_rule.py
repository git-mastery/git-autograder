from typing import List

from git_autograder.answers.answers_record import GitAutograderAnswersRecord
from git_autograder.answers.rules.answer_rule import AnswerRule


class ContainsListRule(AnswerRule):
    def __init__(
        self, values: List[str], subset: bool = True, is_case_sensitive: bool = False
    ) -> None:
        self.values = values
        self.subset = subset
        self.is_case_sensitive = is_case_sensitive

    def apply(self, answer: GitAutograderAnswersRecord) -> None:
        expected = set(
            [v.lower() for v in self.values] if self.is_case_sensitive else self.values
        )
        given = (
            [v.lower() for v in answer.answer_as_list()]
            if self.is_case_sensitive
            else answer.answer_as_list()
        )
        if self.subset and not all([v in expected for v in given]):
            raise Exception(f"Answer for {answer.question} contains an invalid item.")
        elif not any([v in expected for v in given]):
            raise Exception(
                f"Answer for {answer.question} does not contain any valid items."
            )
