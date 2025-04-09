from typing import Optional

from git import Head, Repo


class BranchHelper:
    def __init__(self, repo: Repo) -> None:
        self.repo = repo

    def branch(self, branch_name: str) -> Optional[Head]:
        for head in self.repo.heads:
            if head.name == branch_name:
                return head
        return None

    def has_branch(self, branch_name: str) -> bool:
        return self.branch(branch_name) is not None
