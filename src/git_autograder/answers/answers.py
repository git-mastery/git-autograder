from dataclasses import dataclass
from typing import Dict, List, Optional

from git_autograder.answers.answers_record import GitAutograderAnswersRecord
from git_autograder.answers.rules.answer_rule import AnswerRule
from git_autograder.answers.rules.not_empty_rule import NotEmptyRule
from git_autograder.exception import (
    GitAutograderInvalidStateException,
    GitAutograderWrongAnswerException,
)


@dataclass
class GitAutograderAnswers:
    MISSING_QUESTION = "Missing question {question} in answers file."

    questions: List[str]
    answers: List[str]
    validations: Dict[str, List[AnswerRule]]

    @property
    def qna(self) -> List[GitAutograderAnswersRecord]:
        return list(
            map(
                lambda a: GitAutograderAnswersRecord.from_tuple(a),
                zip(self.questions, self.answers),
            )
        )

    def __getitem__(self, key: int) -> GitAutograderAnswersRecord:
        question = self.questions[key]
        answer = self.answers[key]
        return GitAutograderAnswersRecord.from_tuple((question, answer))

    def __len__(self) -> int:
        return len(self.questions)

    def question_or_none(self, question: str) -> Optional[GitAutograderAnswersRecord]:
        """
        Retrieves the record given a question.

        :returns: GitAutograderAnswersRecord if present, else None.
        :rtype: Optional[GitAutograderAnswersRecord]
        :raises GitAutograderInvalidStateException: if question is not present.
        """
        for i, q in enumerate(self.questions):
            if question == q:
                return GitAutograderAnswersRecord.from_tuple((q, self.answers[i]))
        return None

    def question(self, question: str) -> GitAutograderAnswersRecord:
        """
        Retrieves the record given a question.

        :returns: GitAutograderAnswersRecord if present.
        :rtype: GitAutograderAnswersRecord
        :raises GitAutograderInvalidStateException: if question is not present.
        """
        record = self.question_or_none(question)
        if record is None:
            raise GitAutograderInvalidStateException(
                self.MISSING_QUESTION.format(question=question)
            )
        return record

    def add_validation(
        self, question: str, *rules: AnswerRule
    ) -> "GitAutograderAnswers":
        if question not in self.validations:
            self.validations[question] = []
        self.validations[question] += rules
        return self

    def validate(self) -> None:
        errors: List[str] = []

        for question, validations in self.validations.items():
            answer_record = self.question(question)
            for validation in validations:
                try:
                    validation.apply(answer_record)
                except Exception as e:
                    errors.append(str(e))
                    break

        if errors:
            raise GitAutograderWrongAnswerException(errors)
