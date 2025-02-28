import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import StrEnum
from typing import ClassVar, List, Optional, Tuple

import pytz
from git import Commit, Head, Repo
from git.diff import Lit_change_type

from git_autograder.answers_parser import GitAutograderAnswersParser
from git_autograder.diff import GitAutograderDiff, GitAutograderDiffHelper
from git_autograder.encoder import Encoder


class GitAutograderStatus(StrEnum):
    SUCCESSFUL = "SUCCESSFUL"
    UNSUCCESSFUL = "UNSUCCESSFUL"
    ERROR = "ERROR"


@dataclass
class GitAutograderOutput:
    started_at: datetime
    completed_at: datetime
    is_local: bool
    status: GitAutograderStatus
    comments: Optional[List[str]] = None
    exercise_name: Optional[str] = None

    OUTPUT_FILE_NAME: ClassVar[str] = "output.json"

    def save(self, path: str = "../output") -> None:
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, self.OUTPUT_FILE_NAME)
        output = asdict(self)
        with open(file_path, "w") as f:
            f.write(json.dumps(output, cls=Encoder))


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
            raise Exception("Missing repository name")

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
            raise Exception("No commits")

        assert first_commit is not None

        first_commit_hash = first_commit.hexsha
        start_tag_name = f"git-mastery-start-{first_commit_hash[:7]}"

        start_tag = None
        for tag in self.repo.tags:
            if str(tag) == start_tag_name:
                start_tag = tag
                break

        if start_tag is None:
            raise Exception("Missing start commit")

        return start_tag.commit

    def user_commits(self, branch: str = "main") -> List[Commit]:
        """
        Retrieves only the user commits from a given branch.

        Raises exceptions if the branch has no commits, start tag is not present, or if
        there are no user commits available.
        """
        start_commit = self.start_commit(branch)
        commits = self.commits(branch)
        commits_asc = list(reversed(commits))
        start_commit_index = commits_asc.index(start_commit)
        user_commits = commits_asc[start_commit_index + 1 :]

        if len(user_commits) == 0:
            raise Exception("No user commits found")

        return user_commits

    def save_as_output(
        self, comments: List[str], status: Optional[GitAutograderStatus] = None
    ) -> GitAutograderOutput:
        """
        Saves the GitAutograderRepo as an output file.

        If there is no status provided, the status will be inferred from the comments.
        """
        output = GitAutograderOutput(
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
        output.save()
        if self.is_local:
            print(output)
        return output

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
