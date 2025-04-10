from typing import Optional

from git import Repo

from git_autograder.exception import GitAutograderInvalidStateException
from git_autograder.remote import GitAutograderRemote


class RemoteHelper:
    MISSING_REMOTE = "Remote {remote} is missing."

    def __init__(self, repo: Repo) -> None:
        self.repo = repo

    def remote_or_none(self, remote_name: str) -> Optional[GitAutograderRemote]:
        for remote in self.repo.remotes:
            if remote.name == remote_name:
                return GitAutograderRemote(remote)
        return None

    def remote(self, remote_name: str) -> GitAutograderRemote:
        r = self.remote_or_none(remote_name)
        if r is None:
            raise GitAutograderInvalidStateException(
                self.MISSING_REMOTE.format(remote=remote_name)
            )
        return r

    def has_remote(self, remote_name: str) -> bool:
        return self.remote_or_none(remote_name) is not None
