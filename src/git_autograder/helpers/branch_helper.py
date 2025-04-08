from typing import List

from git import Repo

from git_autograder.exception import GitAutograderInvalidStateException


class BranchHelper:
    def __init__(self, repo: Repo) -> None:
        self.repo = repo

    def track_remote_branches(self, remotes: List[str], strict: bool = False) -> None:
        if "origin" not in [remote.name for remote in self.repo.remotes]:
            return

        tracked = {"main"}
        for remote in self.repo.remote("origin").refs:
            for r in remotes:
                if r not in tracked or f"origin/{r}" != remote.name:
                    continue
                tracked.add(r)
                self.repo.git.checkout("-b", r, f"origin/{r}")
                break

        missed_remotes = list(set(remotes).difference(tracked))
        if len(missed_remotes) > 0 and strict:
            raise GitAutograderInvalidStateException(
                f"Missing branches {', '.join(missed_remotes)} in submission",
            )

    def has_branch(self, branch: str) -> bool:
        return branch in self.repo.heads
