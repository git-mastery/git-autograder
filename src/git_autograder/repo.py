import os

from git import Repo

from git_autograder.helpers.branch_helper import BranchHelper
from git_autograder.helpers.commit_helper import CommitHelper
from git_autograder.helpers.file_helper import FileHelper
from git_autograder.helpers.remote_helper import RemoteHelper


class GitAutograderRepo:
    def __init__(
        self,
        exercise_name: str,
        repo_path: str | os.PathLike,
    ) -> None:
        self.exercise_name = exercise_name
        self.repo_path = repo_path

        self.repo: Repo = Repo(self.repo_path)

        self.branches: BranchHelper = BranchHelper(self.repo)
        self.commits: CommitHelper = CommitHelper(self.repo)
        self.remotes: RemoteHelper = RemoteHelper(self.repo)
        self.files: FileHelper = FileHelper(self.repo)
