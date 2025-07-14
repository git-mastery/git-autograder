import re
from typing import Any, List

from git import Head

from git_autograder.commit import GitAutograderCommit
from git_autograder.diff import GitAutograderDiffHelper
from git_autograder.exception import GitAutograderInvalidStateException
from git_autograder.reflog_entry import GitAutograderReflogEntry


class GitAutograderBranch:
    MISSING_START_COMMIT = "Branch {branch} is missing the Git Mastery start commit"
    MISSING_COMMITS = "Branch {branch} is missing any commits"

    def __init__(self, branch: Head) -> None:
        self.branch = branch

    def __eq__(self, value: Any) -> bool:
        if not isinstance(value, GitAutograderBranch):
            return False
        return value.branch == self.branch

    @property
    def name(self) -> str:
        return self.branch.name

    @property
    def reflog(self) -> List[GitAutograderReflogEntry]:
        output = self.branch.repo.git.reflog("show", self.name).splitlines()
        # We need to dynamically configure the regex
        regex_str = (
            "^([a-f0-9]+)(?: \\(.*\\))? " + self.name + "@\\{(\\d+)\\}: ([^:]+): (.+)$"
        )
        reflog_pattern = re.compile(regex_str)
        entries = []
        for line in output:
            groups = reflog_pattern.match(line)
            if groups:
                sha, index, action, message = groups.groups()
                entries.append(
                    GitAutograderReflogEntry(
                        sha=sha,
                        index=int(index),
                        action=action,
                        message=message,
                    )
                )
        return entries

    @property
    def commits(self) -> List[GitAutograderCommit]:
        """Retrieve the available commits of a given branch."""
        commits: List[GitAutograderCommit] = []
        for commit in self.branch.repo.iter_commits(self.branch):
            commits.append(GitAutograderCommit(commit))

        return commits

    @property
    def start_commit(self) -> GitAutograderCommit:
        """
        Find the Git Mastery start commit from the given branch.

        Raises exceptions if the branch has no commits or if the start tag is not
        present.
        """
        commits = self.commits

        if len(commits) == 0:
            raise GitAutograderInvalidStateException(
                self.MISSING_COMMITS.format(branch=self.name)
            )

        first_commit = commits[-1]
        first_commit_hash = first_commit.hexsha

        start_tag_name = f"git-mastery-start-{first_commit_hash[:7]}"

        start_tag = None
        for tag in self.branch.repo.tags:
            if str(tag) == start_tag_name:
                start_tag = tag
                break

        if start_tag is None:
            raise GitAutograderInvalidStateException(
                self.MISSING_START_COMMIT.format(branch=self.name)
            )

        return GitAutograderCommit(start_tag.commit)

    @property
    def user_commits(self) -> List[GitAutograderCommit]:
        """
        Retrieves only the user commits from a given branch.

        Raises exceptions if the branch has no commits or start tag is not present.
        """
        start_commit = self.start_commit
        commits = self.commits
        commits_asc = list(reversed(commits))
        start_commit_index = commits_asc.index(start_commit)
        user_commits = commits_asc[start_commit_index + 1 :]

        return user_commits

    @property
    def latest_user_commit(self) -> GitAutograderCommit:
        return self.user_commits[-1]

    @property
    def latest_commit(self) -> GitAutograderCommit:
        # This list is sorted in descending order
        return self.commits[0]

    def has_non_empty_commits(self) -> bool:
        """Returns if a given branch has any non-empty commits."""
        for commit in self.user_commits:
            if len(commit.stats.files) > 0:
                return True
        return False

    def has_edited_file(self, file_path: str) -> bool:
        """Returns if a given file has been edited in a given branch."""
        diff_helper = GitAutograderDiffHelper(
            self.start_commit, self.latest_user_commit
        )
        for diff in diff_helper.iter_changes("M"):
            if diff.edited_file_path == file_path:
                return True
        return False

    def has_added_file(self, file_path: str) -> bool:
        """Returns if a given file has been added in a given branch."""
        diff_helper = GitAutograderDiffHelper(
            self.start_commit, self.latest_user_commit
        )
        for diff in diff_helper.iter_changes("A"):
            if diff.edited_file_path == file_path:
                return True
        return False

    def checkout(self) -> None:
        self.branch.checkout()
