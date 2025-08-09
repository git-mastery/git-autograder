from typing import Optional, Union

from git import Repo
from git.types import Commit_ish

from git_autograder.commit import GitAutograderCommit


class CommitHelper:
    def __init__(self, repo: Repo) -> None:
        self.repo = repo

    def commit(self, rev: Optional[Union[Commit_ish, str]]) -> GitAutograderCommit:
        c = self.repo.commit(rev)
        return GitAutograderCommit(c)

    def commit_or_none(
        self, rev: Optional[Union[Commit_ish, str]]
    ) -> Optional[GitAutograderCommit]:
        try:
            c = self.repo.commit(rev)
            return GitAutograderCommit(c)
        except Exception:
            return None
