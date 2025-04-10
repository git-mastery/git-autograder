from typing import Optional

from git import Repo

from git_autograder.branch import GitAutograderBranch
from git_autograder.exception import GitAutograderInvalidStateException


class BranchHelper:
    MISSING_BRANCH = "Branch {branch} is missing."

    def __init__(self, repo: Repo) -> None:
        self.repo = repo

    def branch_or_none(self, branch_name: str) -> Optional[GitAutograderBranch]:
        for head in self.repo.heads:
            if head.name == branch_name:
                return GitAutograderBranch(head)
        return None

    def branch(self, branch_name: str) -> GitAutograderBranch:
        b = self.branch_or_none(branch_name)
        if b is None:
            raise GitAutograderInvalidStateException(
                self.MISSING_BRANCH.format(branch=branch_name)
            )
        return b

    def has_branch(self, branch_name: str) -> bool:
        return self.branch_or_none(branch_name) is not None
