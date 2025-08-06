from abc import ABC, abstractmethod, abstractproperty

from git import Repo

from git_autograder.helpers.branch_helper import BranchHelper
from git_autograder.helpers.commit_helper import CommitHelper
from git_autograder.helpers.file_helper import FileHelper
from git_autograder.helpers.remote_helper import RemoteHelper


class GitAutograderRepoBase(ABC):
    @property
    @abstractmethod
    def repo(self) -> Repo: ...

    @property
    @abstractmethod
    def branches(self) -> BranchHelper: ...

    @property
    @abstractmethod
    def commits(self) -> CommitHelper: ...

    @property
    @abstractmethod
    def remotes(self) -> RemoteHelper: ...

    @property
    @abstractmethod
    def files(self) -> FileHelper: ...
