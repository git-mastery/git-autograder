from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PrContext:
    pr_number: int
    pr_repo_full_name: str


class PrHelperBase(ABC):
    @property
    @abstractmethod
    def pr_number(self) -> int: ...

    @property
    @abstractmethod
    def pr_repo_full_name(self) -> str: ...

    
class PrHelper(PrHelperBase):
    def __init__(self, context: PrContext) -> None:
        self._pr_number = context.pr_number
        self._pr_repo_full_name = context.pr_repo_full_name

    @property
    def pr_number(self) -> int:
        return self._pr_number

    @property
    def pr_repo_full_name(self) -> str:
        return self._pr_repo_full_name
    

class NullPrHelper(PrHelperBase):
    @property
    def pr_number(self) -> int:
        raise AttributeError(
            "Cannot access attribute pr_number on NullPrHelper. Check that your exercise repo's " \
            "pr_context is properly initialized."
        )

    @property
    def pr_repo_full_name(self) -> str:
        raise AttributeError(
            "Cannot access attribute pr_repo_full_name on NullPrHelper. Check that your exercise repo's " \
            "pr_context is properly initialized."
        )