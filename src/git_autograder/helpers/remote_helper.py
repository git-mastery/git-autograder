from typing import List, Optional
from git import Remote, Repo


class RemoteHelper:
    def __init__(self, repo: Repo) -> None:
        self.repo = repo

    def track(self, branches: List[str], remote_name: str = "origin") -> None:
        origin_remote = self.remote(remote_name)
        if origin_remote is None:
            return

        tracked = {"main"}
        for remote in origin_remote.refs:
            for b in branches:
                if b not in tracked or f"{remote_name}/{b}" != remote.name:
                    continue
                tracked.add(b)
                self.repo.git.checkout("-b", b, f"{remote_name}/{b}")
                break

    def remote(self, remote_name: str) -> Optional[Remote]:
        for remote in self.repo.remotes:
            if remote.name == remote_name:
                return remote
        return None

    def has_remote(self, remote_name: str) -> bool:
        return self.remote(remote_name) is not None
