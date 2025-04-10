from typing import Optional

from git import Repo

from git_autograder.remote import GitAutograderRemote


class RemoteHelper:
    def __init__(self, repo: Repo) -> None:
        self.repo = repo

    def remote(self, remote_name: str) -> Optional[GitAutograderRemote]:
        for remote in self.repo.remotes:
            if remote.name == remote_name:
                return GitAutograderRemote(remote)
        return None

    def has_remote(self, remote_name: str) -> bool:
        return self.remote(remote_name) is not None
