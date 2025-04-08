from typing import List

from git_autograder.answers.answers_record import GitAutograderAnswersRecord
from git_autograder.answers.rules.answer_rule import AnswerRule


class HasExactListRule(AnswerRule):
    def __init__(
        self, values: List[str], ordered: bool = False, is_case_sensitive: bool = False
    ) -> None:
        self.values = values
        self.ordered = ordered
        self.is_case_sensitive = is_case_sensitive

    def apply(self, answer: GitAutograderAnswersRecord) -> None:
        expected = (
            [v.lower() for v in self.values] if self.is_case_sensitive else self.values
        )
        given = (
            [v.lower() for v in answer.answer_as_list()]
            if self.is_case_sensitive
            else answer.answer_as_list()
        )
        if self.ordered and expected != given:
            raise Exception(
                f"Answer for {answer.question} does not contain all of the right answers. Ensure that they follow the order specified."
            )
        elif set(expected).intersection(set(given)) != len(expected):
            raise Exception(
                f"Answer for {answer.question} does not contain all of the right answers."
            )
