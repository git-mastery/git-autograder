from typing import List

from git_autograder.answers.answers_record import GitAutograderAnswersRecord
from git_autograder.answers.rules.answer_rule import AnswerRule


class HasExactListRule(AnswerRule):
    INCORRECT_ORDERED = "Answer for {question} does not contian all of the right answers. Ensure that they follow the order specified."
    INCORRECT_UNORDERED = (
        "Answer for {question} does not contain all of the right answers."
    )

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
            raise Exception(self.INCORRECT_ORDERED.format(question=answer.question))
        elif not self.ordered and len(set(expected).intersection(set(given))) != len(
            expected
        ):
            raise Exception(self.INCORRECT_UNORDERED.format(question=answer.question))
