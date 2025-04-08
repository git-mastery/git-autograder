from git_autograder.answers.answers_record import GitAutograderAnswersRecord
from abc import ABC, abstractmethod


class AnswerRule(ABC):
    @abstractmethod
    def apply(self, answer: GitAutograderAnswersRecord) -> None: ...
