from typing import List, Optional, Tuple

from git import Commit, Repo
from git.diff import Lit_change_type

from git_autograder.diff import GitAutograderDiff, GitAutograderDiffHelper
from git_autograder.helpers.branch_helper import BranchHelper
from git_autograder.helpers.commit_helper import CommitHelper


class GraderHelper:
    def __init__(
        self,
        repo: Repo,
        branch_helper: BranchHelper,
        commit_helper: CommitHelper,
    ) -> None:
        self.repo = repo
        self.branch_helper = branch_helper
        self.commit_helper = commit_helper

    def has_non_empty_commits(self, branch: str = "main") -> bool:
        """Returns if a given branch has any non-empty commits."""
        for commit in self.commit_helper.user_commits(branch):
            if len(commit.stats.files) > 0:
                return True
        return False

    def has_edited_file(self, file_path: str, branch: str = "main") -> bool:
        """Returns if a given file has been edited in a given branch."""
        latest_commit = self.commit_helper.user_commits(branch)[-1]
        diff_helper = GitAutograderDiffHelper(
            self.commit_helper.start_commit(branch), latest_commit
        )
        for diff in diff_helper.iter_changes("M"):
            if diff.edited_file_path == file_path:
                return True
        return False

    def has_added_file(self, file_path: str, branch: str = "main") -> bool:
        """Returns if a given file has been added in a given branch."""
        latest_commit = self.commit_helper.user_commits(branch)[-1]
        diff_helper = GitAutograderDiffHelper(
            self.commit_helper.start_commit(branch), latest_commit
        )
        for diff in diff_helper.iter_changes("A"):
            if diff.edited_file_path == file_path:
                return True
        return False

    def get_file_diff(
        self, a: Commit, b: Commit, file_path: str
    ) -> Optional[Tuple[GitAutograderDiff, Lit_change_type]]:
        """Returns file difference between two commits across ALL change types."""
        # Based on the expectation that there can only exist one change type per file in a diff
        diff_helper = GitAutograderDiffHelper(a, b)
        change_types: List[Lit_change_type] = ["A", "D", "R", "M", "T"]
        for change_type in change_types:
            for change in diff_helper.iter_changes(change_type):
                if change.diff_parser is None or change.edited_file_path != file_path:
                    continue
                return change, change_type
        return None
