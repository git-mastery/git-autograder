from typing import Optional

from git import Repo

from git_autograder.exception import GitAutograderInvalidStateException


class PrHelper:
    MISSING_PR = "PR {pr} is missing."

    def __init__(self, repo: Repo) -> None:
        self.repo = repo
