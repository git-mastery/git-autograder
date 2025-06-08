import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pytz
from git import Repo

from git_autograder.answers.answers import GitAutograderAnswers
from git_autograder.answers.answers_parser import GitAutograderAnswersParser
from git_autograder.exception import (
    GitAutograderInvalidStateException,
    GitAutograderWrongAnswerException,
)
from git_autograder.helpers.branch_helper import BranchHelper
from git_autograder.helpers.commit_helper import CommitHelper
from git_autograder.helpers.file_helper import FileHelper
from git_autograder.helpers.remote_helper import RemoteHelper
from git_autograder.output import GitAutograderOutput
from git_autograder.status import GitAutograderStatus


class GitAutograderRepo:
    def __init__(
        self,
        exercise_name: str,
        repo_path: str | os.PathLike,
    ) -> None:
        # TODO: We should not be starting the grading at the point of initializing, but
        # we're keeping this because of the exception system
        self.started_at = self.__now()
        self.exercise_name = exercise_name
        self.repo_path = repo_path

        self.repo: Repo = Repo(self.repo_path)

        self.branches: BranchHelper = BranchHelper(self.repo)
        self.commits: CommitHelper = CommitHelper(self.repo)
        self.remotes: RemoteHelper = RemoteHelper(self.repo)
        self.files: FileHelper = FileHelper(self.repo)
        self.__answers_parser: Optional[GitAutograderAnswersParser] = None
        self.__answers: Optional[GitAutograderAnswers] = None

    @property
    def answers(self) -> GitAutograderAnswers:
        """Parses a QnA file (answers.txt). Verifies that the file exists."""
        # We need to use singleton patterns here since we want to avoid repeatedly parsing
        # These are all optional to start since the grader might not require answers
        if self.__answers_parser is None:
            answers_file_path = Path(self.repo_path) / "answers.txt"
            # Use singleton for answers parser
            try:
                self.__answers_parser = GitAutograderAnswersParser(answers_file_path)
            except Exception as e:
                raise GitAutograderInvalidStateException(
                    str(e),
                )

        if self.__answers is None:
            self.__answers = self.__answers_parser.answers

        return self.__answers

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
            exercise_name=self.exercise_name,
            started_at=self.started_at,
            completed_at=self.__now(),
            comments=comments,
            status=(
                GitAutograderStatus.SUCCESSFUL
                if len(comments) == 0
                else GitAutograderStatus.UNSUCCESSFUL
            )
            if status is None
            else status,
        )

    def wrong_answer(self, comments: List[str]) -> GitAutograderWrongAnswerException:
        return GitAutograderWrongAnswerException(comments)
