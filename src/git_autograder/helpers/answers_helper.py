from typing import List

from git_autograder.answers import GitAutograderAnswers
from git_autograder.answers.rules import AnswerRule
from git_autograder.exception import (
    GitAutograderInvalidStateException,
    GitAutograderWrongAnswerException,
)
from git_autograder.repo_context import GitAutograderRepoContext


class AnswersHelper:
    def __init__(
        self, ctx: GitAutograderRepoContext, answers: GitAutograderAnswers
    ) -> None:
        self.ctx = ctx
        self.answers = answers

    def validate_question(
        self, question: str, rules: List[AnswerRule]
    ) -> "AnswersHelper":
        answer = self.answers.get_by_question(question)
        if answer is None:
            raise GitAutograderInvalidStateException(
                f"Missing question {question} in answers file.",
                exercise_name=self.ctx.exercise_name,
                is_local=self.ctx.is_local,
                started_at=self.ctx.started_at,
            )

        for rule in rules:
            try:
                rule.apply(answer)
            except Exception as e:
                raise GitAutograderWrongAnswerException(
                    [str(e)],
                    exercise_name=self.ctx.exercise_name,
                    is_local=self.ctx.is_local,
                    started_at=self.ctx.started_at,
                )

        return self
