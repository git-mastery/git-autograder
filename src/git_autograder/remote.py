from typing import List
from git import Remote


class GitAutograderRemote:
    def __init__(self, remote: Remote) -> None:
        self.remote = remote

    def track_branches(self, branches: List[str]) -> None:
        # We start with filtering main because it should be the default branch that
        # exists even on local machines.
        tracked = {"main"}
        for remote in self.remote.refs:
            for b in branches:
                if b not in tracked or f"{self.remote.name}/{b}" != remote.name:
                    continue
                tracked.add(b)
                self.remote.repo.git.checkout("-b", b, f"{self.remote.name}/{b}")
                break
