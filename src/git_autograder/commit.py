from typing import Any, Union

from git import Commit, Stats


class GitAutograderCommit:
    def __init__(self, commit: Commit) -> None:
        self.commit = commit

    def __eq__(self, value: Any) -> bool:
        if not isinstance(value, GitAutograderCommit):
            return False
        return value.commit == self.commit

    @property
    def hexsha(self) -> str:
        return self.commit.hexsha

    @property
    def stats(self) -> Stats:
        return self.commit.stats

    def is_child(self, parent: Union[Commit, "GitAutograderCommit"]) -> bool:
        def _is_child(child: Commit, parent: Commit) -> bool:
            if child == parent:
                return True

            res = False
            for child_parent in child.parents:
                res |= _is_child(child_parent, parent)

            return res

        return _is_child(
            self.commit, parent if isinstance(parent, Commit) else parent.commit
        )
