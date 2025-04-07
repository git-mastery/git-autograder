from typing import List
from git_autograder.exception import GitAutograderInvalidStateException
from git_autograder.repo_context import GitAutograderRepoContext


class BranchHelper:
    def __init__(self, ctx: GitAutograderRepoContext) -> None:
        self.ctx = ctx

    def track_remote_branches(self, remotes: List[str], strict: bool = False) -> None:
        if self.ctx.is_local:
            return

        tracked = {"main"}
        for remote in self.ctx.repo.repo.remote("origin").refs:
            for r in remotes:
                if r not in tracked or f"origin/{r}" != remote.name:
                    continue
                tracked.add(r)
                self.ctx.repo.repo.git.checkout("-b", r, f"origin/{r}")
                break

        missed_remotes = list(set(remotes).difference(tracked))
        if len(missed_remotes) > 0 and strict:
            raise GitAutograderInvalidStateException(
                f"Missing branches {', '.join(missed_remotes)} in submission",
                self.ctx.exercise_name,
                self.ctx.started_at,
                self.ctx.is_local,
            )

    def has_branch(self, branch: str) -> bool:
        return branch in self.ctx.repo.repo.heads
