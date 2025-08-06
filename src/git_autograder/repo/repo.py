import os

from git import Repo

from git_autograder.helpers.branch_helper import BranchHelper
from git_autograder.helpers.commit_helper import CommitHelper
from git_autograder.helpers.file_helper import FileHelper
from git_autograder.helpers.remote_helper import RemoteHelper
from git_autograder.repo.repo_base import GitAutograderRepoBase


class GitAutograderRepo(GitAutograderRepoBase):
    def __init__(
        self,
        exercise_name: str,
        repo_path: str | os.PathLike,
    ) -> None:
        self.exercise_name = exercise_name
        self.repo_path = repo_path

        self._repo: Repo = Repo(self.repo_path)

        self._branches: BranchHelper = BranchHelper(self._repo)
        self._commits: CommitHelper = CommitHelper(self._repo)
        self._remotes: RemoteHelper = RemoteHelper(self._repo)
        self._files: FileHelper = FileHelper(self._repo)

    @property
    def repo(self) -> Repo:
        return self._repo

    @property
    def branches(self) -> BranchHelper:
        return self._branches

    @property
    def commits(self) -> CommitHelper:
        return self._commits

    @property
    def remotes(self) -> RemoteHelper:
        return self._remotes

    @property
    def files(self) -> FileHelper:
        return self._files
