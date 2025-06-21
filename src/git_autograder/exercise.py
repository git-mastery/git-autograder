import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional

import pytz

from git_autograder.answers.answers import GitAutograderAnswers
from git_autograder.answers.answers_parser import GitAutograderAnswersParser
from git_autograder.exception import (
    GitAutograderInvalidStateException,
    GitAutograderWrongAnswerException,
)
from git_autograder.exercise_config import ExerciseConfig
from git_autograder.output import GitAutograderOutput
from git_autograder.repo import GitAutograderRepo
from git_autograder.status import GitAutograderStatus


class GitAutograderExercise:
    def __init__(
        self,
        exercise_path: str | os.PathLike,
    ) -> None:
        # TODO: We should not be starting the grading at the point of initializing, but
        # we're keeping this because of the exception system
        self.started_at = self.__now()
        self.exercise_path = exercise_path

        exercise_config_path = Path(exercise_path) / ".gitmastery-exercise.json"
        if not os.path.isfile(exercise_config_path):
            raise GitAutograderInvalidStateException(
                "Missing .gitmastery-exercise.json"
            )

        self.config = ExerciseConfig.read_config(exercise_config_path)

        self.exercise_name = self.config.exercise_name
        if (
            self.config.exercise_repo.init
            or self.config.exercise_repo.repo_type == "remote"
        ):
            # Only initialize the sub-folder as a Git repository when we're sure that
            # it will be a Git repository
            self.repo: Optional[GitAutograderRepo] = GitAutograderRepo(
                self.config.exercise_name, self.config.exercise_repo.repo_name
            )
        self.__answers_parser: Optional[GitAutograderAnswersParser] = None
        self.__answers: Optional[GitAutograderAnswers] = None

    @property
    def answers(self) -> GitAutograderAnswers:
        """Parses a QnA file (answers.txt). Verifies that the file exists."""
        # We need to use singleton patterns here since we want to avoid repeatedly parsing
        # These are all optional to start since the grader might not require answers
        if self.__answers_parser is None:
            answers_file_path = Path(self.exercise_path) / "answers.txt"
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
        self, comments: List[str], status: GitAutograderStatus
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
            status=status,
        )

    def wrong_answer(self, comments: List[str]) -> GitAutograderWrongAnswerException:
        return GitAutograderWrongAnswerException(comments)
