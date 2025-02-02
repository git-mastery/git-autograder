import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import StrEnum
from typing import ClassVar, List, Optional

import pytz
from git_autograder.answers_parser import GitAutograderAnswersParser
from git_autograder.encoder import Encoder
from git import Repo, Commit


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
    def __init__(self, require_answers: bool = False, branch: str = "main") -> None:
        self.__branch = branch
        self.__started_at = self.__now()
        self.__is_local: bool = os.environ.get("is_local", "false") == "true"
        self.__exercise_name = os.environ.get("repository_name")
        self.__require_answers = require_answers

        if self.__exercise_name is None:
            raise Exception("Missing repository name")

        self.repo: Repo = (
            Repo("../main/")
            if not self.__is_local
            else Repo(f"../exercises/{self.__exercise_name}")
        )

        commits = []
        first_commit = None
        for commit in self.repo.iter_commits(self.__branch):
            first_commit = commit
            commits.append(commit)

        if first_commit is None:
            raise Exception("Missing first commit")

        first_commit_hash = first_commit.hexsha
        start_tag_name = f"git-mastery-start-{first_commit_hash[:7]}"

        start_tag = None
        for tag in self.repo.tags:
            if str(tag) == start_tag_name:
                start_tag = tag
                break

        if start_tag is None:
            raise Exception("Missing start tag")

        self.start_commit: Commit = start_tag.commit
        commits_asc = list(reversed(commits))
        start_commit_index = commits_asc.index(self.start_commit)
        self.user_commits: List[Commit] = commits_asc[start_commit_index + 1 :]

        if len(self.user_commits) == 0:
            raise Exception("No user commits found")

        if self.__require_answers:
            self.answers = GitAutograderAnswersParser()

    @staticmethod
    def __now() -> datetime:
        return datetime.now(tz=pytz.UTC)

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
            is_local=self.__is_local,
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
        if self.__is_local:
            print(output)
        return output
