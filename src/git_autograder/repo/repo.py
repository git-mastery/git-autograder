import os
from pathlib import Path
from typing import Optional

from git import Repo

from git_autograder.exercise_config import ExerciseConfig
from git_autograder.helpers.branch_helper import BranchHelper
from git_autograder.helpers.commit_helper import CommitHelper
from git_autograder.helpers.file_helper import FileHelper
from git_autograder.helpers.pr_helper.null_pr_helper import NullPrHelper
from git_autograder.helpers.pr_helper.pr_helper import PrContext, PrHelper
from git_autograder.helpers.remote_helper import RemoteHelper
from git_autograder.helpers.tag_helper import TagHelper
from git_autograder.repo.repo_base import GitAutograderRepoBase


class GitAutograderRepo(GitAutograderRepoBase):
    def __init__(
        self,
        exercise_name: str,
        repo_path: str | os.PathLike,
        pr_context: Optional[PrContext] = None,
    ) -> None:
        self.exercise_name = exercise_name
        self.repo_path = repo_path

        self._repo: Repo = Repo(self.repo_path)

        self._branches: BranchHelper = BranchHelper(self._repo)
        self._commits: CommitHelper = CommitHelper(self._repo)
        self._remotes: RemoteHelper = RemoteHelper(self._repo)
        self._files: FileHelper = FileHelper(self._repo)
        self._tags: TagHelper = TagHelper(self._repo)
        self._prs: PrHelper | NullPrHelper = PrHelper(pr_context, self._repo) if pr_context else NullPrHelper()

    @property
    def repo(self) -> Repo:
        return self._repo

    @property
    def branches(self) -> BranchHelper:
        return self._branches

    @property
    def commits(self) -> CommitHelper:
        return self._commits

    @property
    def remotes(self) -> RemoteHelper:
        return self._remotes

    @property
    def files(self) -> FileHelper:
        return self._files
    
    @property
    def tags(self) -> TagHelper:
        return self._tags
    
    @property
    def prs(self) -> PrHelper | NullPrHelper:
        return self._prs

    @staticmethod
    def read_pr_context_from_config(
        repo_path: Optional[str | os.PathLike] = None, 
        config: Optional[ExerciseConfig] = None
    ) -> Optional[PrContext]:
        if config is None:
            if repo_path is None:
                return None
            config_path = Path(repo_path).parent / ".gitmastery-exercise.json"
            if not config_path.is_file():
                return None
            config = ExerciseConfig.read_config(config_path)
            
        try:
            pr_number = config.exercise_repo.pr_number
            pr_repo_full_name = config.exercise_repo.pr_repo_full_name
        except (KeyError, AttributeError):
            return None
        
        if pr_number is None or pr_repo_full_name is None:
            return None        
        return PrContext(pr_number=pr_number, pr_repo_full_name=pr_repo_full_name)
    
    def refresh_pr_helper(self) -> None:
        pr_context = GitAutograderRepo.read_pr_context_from_config(repo_path=self.repo_path)
        self._prs = (
            PrHelper(pr_context, self._repo)
            if pr_context
            else NullPrHelper()
        )
