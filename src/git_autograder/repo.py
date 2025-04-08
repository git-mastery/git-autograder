from dataclasses import dataclass
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pytz
from git import Repo

from git_autograder.answers.answers_parser import GitAutograderAnswersParser
from git_autograder.exception import (
    GitAutograderInvalidStateException,
    GitAutograderWrongAnswerException,
)
from git_autograder.helpers.answers_helper import AnswersHelper
from git_autograder.helpers.branch_helper import BranchHelper
from git_autograder.helpers.commit_helper import CommitHelper
from git_autograder.helpers.grader_helper import GraderHelper
from git_autograder.output import GitAutograderOutput
from git_autograder.status import GitAutograderStatus


class GitAutograderRepo:
    @dataclass
    class Context:
        repo: "GitAutograderRepo"
        is_local: bool
        exercise_name: str
        started_at: datetime
        repo_path: Optional[str | os.PathLike] = None

    def __init__(
        self,
        is_local: bool,
        exercise_name: str,
        repo_path: Optional[str | os.PathLike] = None,
    ) -> None:
        # TODO: We should not be starting the grading at the point of initializing, but we're keeping this because of the exception system
        self.__started_at = self.__now()
        self.is_local: bool = is_local
        self.__exercise_name = exercise_name
        self.__repo_path = (
            repo_path
            if repo_path is not None
            else Path.cwd().parent / "main"
            if not is_local
            else Path.cwd().parent / "exercises" / exercise_name
        )

        self.repo: Repo = Repo(self.__repo_path)
        self.ctx = self.Context(
            repo=self,
            started_at=self.__started_at,
            is_local=self.is_local,
            repo_path=self.__repo_path,
            exercise_name=self.__exercise_name,
        )
        self.branches: BranchHelper = BranchHelper(self.ctx)
        self.commits: CommitHelper = CommitHelper(self.ctx)
        self.grader: GraderHelper = GraderHelper(self.ctx, self.branches, self.commits)
        self.__answers_parser: Optional[GitAutograderAnswersParser] = None
        self.__answers: Optional[AnswersHelper] = None

    @property
    def answers(self) -> AnswersHelper:
        """Parses a QnA file (answers.txt). Verifies that the file exists."""
        # We need to use singleton patterns here since we want to avoid repeatedly parsing
        # These are all optional to start since the grader might not require answers
        if self.__answers_parser is None:
            answers_file_path = Path(self.__repo_path) / "answers.txt"
            # Use singleton for answers parser
            try:
                self.__answers_parser = GitAutograderAnswersParser(answers_file_path)
            except Exception as e:
                raise GitAutograderInvalidStateException(
                    str(e),
                    exercise_name=self.__exercise_name,
                    is_local=self.is_local,
                    started_at=self.__started_at,
                )

        if self.__answers is None:
            self.__answers = AnswersHelper(self.ctx, self.__answers_parser.answers)

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

    def wrong_answer(self, comments: List[str]) -> GitAutograderWrongAnswerException:
        return GitAutograderWrongAnswerException(
            comments, self.__exercise_name, self.__started_at, self.is_local
        )
