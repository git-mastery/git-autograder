from abc import ABC, abstractmethod

from git_autograder.answers.answers_record import GitAutograderAnswersRecord


class AnswerRule(ABC):
    @abstractmethod
    def apply(self, answer: GitAutograderAnswersRecord) -> None: ...
