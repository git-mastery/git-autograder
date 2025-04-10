from typing import Optional

from git import Repo

from git_autograder.branch import GitAutograderBranch


class BranchHelper:
    def __init__(self, repo: Repo) -> None:
        self.repo = repo

    def branch(self, branch_name: str) -> Optional[GitAutograderBranch]:
        for head in self.repo.heads:
            if head.name == branch_name:
                return GitAutograderBranch(head)
        return None

    def has_branch(self, branch_name: str) -> bool:
        return self.branch(branch_name) is not None
