from typing import List

from git import Repo

from git_autograder.answers import GitAutograderAnswers
from git_autograder.answers.rules import AnswerRule
from git_autograder.exception import (
    GitAutograderInvalidStateException,
    GitAutograderWrongAnswerException,
)


class AnswersHelper:
    def __init__(self, repo: Repo, answers: GitAutograderAnswers) -> None:
        self.repo = repo
        self.answers = answers

    def validate_question(
        self, question: str, rules: List[AnswerRule]
    ) -> "AnswersHelper":
        answer = self.answers.get_by_question(question)
        if answer is None:
            raise GitAutograderInvalidStateException(
                f"Missing question {question} in answers file.",
            )

        for rule in rules:
            try:
                rule.apply(answer)
            except Exception as e:
                raise GitAutograderWrongAnswerException(
                    [str(e)],
                )

        return self
