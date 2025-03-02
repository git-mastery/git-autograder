import os
from datetime import datetime
from typing import List, Optional, Tuple

import pytz
from git import Commit, Repo
from git.diff import Lit_change_type

from git_autograder.answers_parser import GitAutograderAnswersParser
from git_autograder.diff import GitAutograderDiff, GitAutograderDiffHelper
from git_autograder.exception import (
    GitAutograderInvalidStateException,
    GitAutograderWrongAnswerException,
)
from git_autograder.status import GitAutograderStatus
from git_autograder.output import GitAutograderOutput


class GitAutograderRepo:
    def __init__(
        self,
        repo_path: Optional[str | os.PathLike] = None,
    ) -> None:
        self.__started_at = self.__now()
        self.is_local: bool = os.environ.get("is_local", "false") == "true"
        self.__exercise_name = os.environ.get("repository_name")
        self.__repo_path = repo_path

        if self.__exercise_name is None:
            raise GitAutograderInvalidStateException(
                "Missing repository name",
                self.__exercise_name,
                self.__started_at,
                self.is_local,
            )

        # TODO Set this up to be more dynamic
        self.repo: Repo = (
            Repo(self.__repo_path)
            if self.__repo_path is not None
            else (
                Repo("../main")
                if not self.is_local
                else Repo(f"../exercises/{self.__exercise_name}")
            )
        )

    @staticmethod
    def __now() -> datetime:
        return datetime.now(tz=pytz.UTC)

    def to_output(
        self, comments: List[str], status: Optional[GitAutograderStatus] = None
    ) -> GitAutograderOutput:
        """
        Creates a GitAutograderOutput object.

        If there is no status provided, the status will be inferred from the comments.
        """
        return GitAutograderOutput(
            exercise_name=self.__exercise_name,
            started_at=self.__started_at,
            completed_at=self.__now(),
            is_local=self.is_local,
            comments=comments,
            status=(
                GitAutograderStatus.SUCCESSFUL
                if len(comments) == 0
                else GitAutograderStatus.UNSUCCESSFUL
            )
            if status is None
            else status,
        )

    def wrong_answer(self, comments: List[str]) -> None:
        raise GitAutograderWrongAnswerException(
            comments, self.__exercise_name, self.__started_at, self.is_local
        )

    def track_remote_branches(self, remotes: List[str], strict: bool = False) -> None:
        if self.is_local:
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
                self.__exercise_name,
                self.__started_at,
                self.is_local,
            )

    def answers(self) -> GitAutograderAnswersParser:
        """Parses a QnA file (answers.txt). Verifies that the file exists."""
        return (
            GitAutograderAnswersParser(f"{self.__repo_path}/answers.txt")
            if self.__repo_path is not None
            else GitAutograderAnswersParser("../main/answers.txt")
            if not self.is_local
            else GitAutograderAnswersParser(
                f"../exercises/{self.__exercise_name}/answers.txt"
            )
        )

    def commits(self, branch: str = "main") -> List[Commit]:
        """Retrieve the available commits of a given branch."""
        commits = []
        for commit in self.repo.iter_commits(branch):
            commits.append(commit)

        return commits

    def start_commit(self, branch: str = "main") -> Commit:
        """
        Find the Git Mastery start commit from the given branch.

        Raises exceptions if the branch has no commits or if the start tag is not
        present.
        """
        first_commit = None
        commits = self.commits(branch)
        for commit in self.repo.iter_commits(branch):
            first_commit = commit
            commits.append(commit)

        if len(commits) == 0:
            raise GitAutograderInvalidStateException(
                f"Branch {branch} is missing any commits",
                self.__exercise_name,
                self.__started_at,
                self.is_local,
            )

        assert first_commit is not None

        first_commit_hash = first_commit.hexsha
        start_tag_name = f"git-mastery-start-{first_commit_hash[:7]}"

        start_tag = None
        for tag in self.repo.tags:
            if str(tag) == start_tag_name:
                start_tag = tag
                break

        if start_tag is None:
            raise GitAutograderInvalidStateException(
                f"Branch {branch} is missing the Git Mastery start commit",
                self.__exercise_name,
                self.__started_at,
                self.is_local,
            )

        return start_tag.commit

    def user_commits(self, branch: str = "main") -> List[Commit]:
        """
        Retrieves only the user commits from a given branch.

        Raises exceptions if the branch has no commits or start tag is not present.
        """
        start_commit = self.start_commit(branch)
        commits = self.commits(branch)
        commits_asc = list(reversed(commits))
        start_commit_index = commits_asc.index(start_commit)
        user_commits = commits_asc[start_commit_index + 1 :]

        return user_commits

    def has_non_empty_commits(self, branch: str = "main") -> bool:
        """Returns if a given branch has any non-empty commits."""
        for commit in self.user_commits(branch):
            if len(commit.stats.files) > 0:
                return True
        return False

    def has_edited_file(self, file_path: str, branch: str = "main") -> bool:
        """Returns if a given file has been edited in a given branch."""
        latest_commit = self.user_commits(branch)[-1]
        diff_helper = GitAutograderDiffHelper(self.start_commit(branch), latest_commit)
        for diff in diff_helper.iter_changes("M"):
            if diff.edited_file_path == file_path:
                return True
        return False

    def has_added_file(self, file_path: str, branch: str = "main") -> bool:
        """Returns if a given file has been added in a given branch."""
        latest_commit = self.user_commits(branch)[-1]
        diff_helper = GitAutograderDiffHelper(self.start_commit(branch), latest_commit)
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

    def has_branch(self, branch: str) -> bool:
        return branch in self.repo.heads

    def is_child_commit(self, child: Commit, commit: Commit) -> bool:
        if child == commit:
            return True

        res = False
        for parent in child.parents:
            res |= self.is_child_commit(parent, commit)

        return res
