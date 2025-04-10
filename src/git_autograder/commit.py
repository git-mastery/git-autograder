from typing import List, Optional, Tuple, Union

from git import Commit, Stats
from git.diff import Lit_change_type

from git_autograder.diff.diff import GitAutograderDiff
from git_autograder.diff.diff_helper import GitAutograderDiffHelper


class GitAutograderCommit:
    def __init__(self, commit: Commit) -> None:
        self.commit = commit

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

    def get_file_diff(
        self, other: Union[Commit, "GitAutograderCommit"], file_path: str
    ) -> Optional[Tuple[GitAutograderDiff, Lit_change_type]]:
        """Returns file difference between two commits across ALL change types."""
        # Based on the expectation that there can only exist one change type per file in a diff
        diff_helper = GitAutograderDiffHelper(self, other)
        change_types: List[Lit_change_type] = ["A", "D", "R", "M", "T"]
        for change_type in change_types:
            for change in diff_helper.iter_changes(change_type):
                if change.diff_parser is None or change.edited_file_path != file_path:
                    continue
                return change, change_type
        return None
