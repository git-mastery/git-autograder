from dataclasses import dataclass
from typing import List, Optional

from git_autograder.answers.answers_record import GitAutograderAnswersRecord
from git_autograder.answers.rules.answer_rule import AnswerRule
from git_autograder.exception import (
    GitAutograderInvalidStateException,
    GitAutograderWrongAnswerException,
)


@dataclass
class GitAutograderAnswers:
    MISSING_QUESTION = "Missing question {question} in answers file."

    questions: List[str]
    answers: List[str]

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

    def validate_question(
        self, question: str, rules: List[AnswerRule]
    ) -> "GitAutograderAnswers":
        """
        Validates that a given GitAutograderAnswersRecord passes a set of rules.

        :raises GitAutograderWrongAnswerException: when a rule is violated.
        """
        q = self.question(question)

        for rule in rules:
            try:
                rule.apply(q)
            except Exception as e:
                raise GitAutograderWrongAnswerException([str(e)])

        return self
