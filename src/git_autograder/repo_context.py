from dataclasses import dataclass
from datetime import datetime
import os
from typing import Optional
from git_autograder.repo import GitAutograderRepo


@dataclass
class GitAutograderRepoContext:
    repo: GitAutograderRepo
    is_local: bool
    exercise_name: str
    started_at: datetime
    repo_path: Optional[str | os.PathLike] = None
