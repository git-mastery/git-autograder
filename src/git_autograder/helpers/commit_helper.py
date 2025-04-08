from typing import List

from git import Commit, Repo

from git_autograder.exception import GitAutograderInvalidStateException


class CommitHelper:
    def __init__(self, repo: Repo) -> None:
        self.repo = repo

    def is_child_commit(self, child: Commit, parent: Commit) -> bool:
        if child == parent:
            return True

        res = False
        for parent in child.parents:
            res |= self.is_child_commit(parent, parent)

        return res

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
        commits = self.commits(branch)

        if len(commits) == 0:
            raise GitAutograderInvalidStateException(
                f"Branch {branch} is missing any commits",
            )

        first_commit = commits[-1]

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
