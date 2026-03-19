from dataclasses import dataclass
from git import Repo
from git_autograder.helpers.pr_helper.pr_helper_base import PrHelperBase
from git_autograder.pr import GitAutograderPr


@dataclass(frozen=True)
class PrContext:
    pr_number: int
    pr_repo_full_name: str


class PrHelper(PrHelperBase):
    def __init__(self, context: PrContext, repo: Repo) -> None:
        self._pr_number = context.pr_number
        self._pr_repo_full_name = context.pr_repo_full_name
        self._pr = GitAutograderPr.fetch(
            pr_number=self._pr_number,
            pr_repo_full_name=self._pr_repo_full_name,
            repo=repo,
        )

    @property
    def pr(self) -> GitAutograderPr:
        return self._pr
    