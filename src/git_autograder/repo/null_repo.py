from git import Repo

from git_autograder.helpers.branch_helper import BranchHelper
from git_autograder.helpers.commit_helper import CommitHelper
from git_autograder.helpers.file_helper import FileHelper
from git_autograder.helpers.remote_helper import RemoteHelper
from git_autograder.repo.repo_base import GitAutograderRepoBase


class NullGitAutograderRepo(GitAutograderRepoBase):
    @property
    def repo(self) -> Repo:
        raise AttributeError(
            "Cannot access attribute repo on NullGitAutograderRepo. Check that your repo_type is not 'ignore'."
        )

    @property
    def branches(self) -> BranchHelper:
        raise AttributeError(
            "Cannot access attribute branches on NullGitAutograderRepo. Check that your repo_type is not 'ignore'."
        )

    @property
    def commits(self) -> CommitHelper:
        raise AttributeError(
            "Cannot access attribute commits on NullGitAutograderRepo. Check that your repo_type is not 'ignore'."
        )

    @property
    def remotes(self) -> RemoteHelper:
        raise AttributeError(
            "Cannot access attribute remotes on NullGitAutograderRepo. Check that your repo_type is not 'ignore'."
        )

    @property
    def files(self) -> FileHelper:
        raise AttributeError(
            "Cannot access attribute files on NullGitAutograderRepo. Check that your repo_type is not 'ignore'."
        )

    def __getattr__(self, name: str) -> None:
        raise AttributeError(
            f"Cannot access attribute {name} on NullGitAutograderRepo. Check that your repo_type is not 'ignore'."
        )
