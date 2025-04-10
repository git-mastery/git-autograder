from dataclasses import dataclass
from typing import List, Tuple

from git_autograder.answers.rules.answer_rule import AnswerRule
from git_autograder.exception import GitAutograderWrongAnswerException


@dataclass
class GitAutograderAnswersRecord:
    question: str
    answer: str

    def as_tuple(self) -> Tuple[str, str]:
        return self.question, self.answer

    @staticmethod
    def from_tuple(tuple_value: Tuple[str, str]) -> "GitAutograderAnswersRecord":
        return GitAutograderAnswersRecord(
            question=tuple_value[0], answer=tuple_value[1]
        )

    def answer_as_list(self) -> List[str]:
        points: List[str] = []
        acc = ""
        for line in self.answer.split("\n"):
            if line.startswith("-"):
                if acc.strip() != "":
                    points.append(acc.strip()[::])
                acc = line[1:].strip() + "\n"
            else:
                acc += line + "\n"
        if acc.strip() != "":
            points.append(acc.strip()[::])
        return points

    def validate(self, rules: List[AnswerRule]) -> None:
        """
        Validates that a given GitAutograderAnswersRecord passes a set of rules.

        :raises GitAutograderWrongAnswerException: when a rule is violated.
        """
        for rule in rules:
            try:
                rule.apply(self)
            except Exception as e:
                raise GitAutograderWrongAnswerException([str(e)])
