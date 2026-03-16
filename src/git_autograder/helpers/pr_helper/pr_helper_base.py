from abc import ABC, abstractmethod

from git_autograder.pr import GitAutograderPr


class PrHelperBase(ABC):
    @property
    @abstractmethod
    def pr(self) -> GitAutograderPr: ...
