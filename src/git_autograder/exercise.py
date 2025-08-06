import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import pytz
from git import InvalidGitRepositoryError

from git_autograder.answers.answers import GitAutograderAnswers
from git_autograder.answers.answers_parser import GitAutograderAnswersParser
from git_autograder.exception import (
    GitAutograderInvalidStateException,
    GitAutograderWrongAnswerException,
)
from git_autograder.exercise_config import ExerciseConfig
from git_autograder.output import GitAutograderOutput
from git_autograder.repo.null_repo import NullGitAutograderRepo
from git_autograder.repo.repo import GitAutograderRepo
from git_autograder.repo.repo_base import GitAutograderRepoBase
from git_autograder.status import GitAutograderStatus


class GitAutograderExercise:
    """This is the central Git-Mastery exercise grading layer. It essentially provides a
    central layer to create autograding for a given exercise.

    Exercises have the following folder structure::

        exercise_root/
        |_ README.md
        |_ .gitmastery-exercise.json
        |_ *resource_files
        |_ repo/
        |_ .git/

    :param exercise_path: Path to a given exercise folder
    :type exercise_path: Union[str, os.PathLike]
    """

    def __init__(
        self,
        exercise_path: str | os.PathLike,
    ) -> None:
        """Constructor method"""

        # TODO: We should not be starting the grading at the point of initializing, but
        # we're keeping this because of the exception system
        self.started_at = self.__now()
        self.exercise_path = exercise_path

        self.exercise_config_path = Path(exercise_path) / ".gitmastery-exercise.json"
        if not self.has_exercise_config(self.exercise_config_path):
            raise GitAutograderInvalidStateException(
                "Missing .gitmastery-exercise.json"
            )

        self.config = ExerciseConfig.read_config(self.exercise_config_path)

        self.exercise_name = self.config.exercise_name
        try:
            # We can always make the assumption that when verifying, we should always
            # first have a Git repository.
            # The only edge cases are those where they run git init themselves, but that
            # is the purpose of handling the exception where we can display an error on
            # their end.
            self.repo: GitAutograderRepoBase
            if self.config.exercise_repo.repo_type == "ignore":
                self.repo = NullGitAutograderRepo()
            else:
                self.repo = GitAutograderRepo(
                    self.config.exercise_name,
                    Path(exercise_path) / self.config.exercise_repo.repo_name,
                )
        except InvalidGitRepositoryError:
            raise GitAutograderInvalidStateException("Exercise is not a Git repository")
        self.__answers_parser: Optional[GitAutograderAnswersParser] = None
        self.__answers: Optional[GitAutograderAnswers] = None

    @property
    def answers(self) -> GitAutograderAnswers:
        """Parses a QnA file (answers.txt). Verifies that the file exists."""
        if self.__answers is not None:
            return self.__answers

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

    def has_exercise_config(self, exercise_config_path: str | Path) -> bool:
        # Separate method because it's easier to mock the result
        return os.path.isfile(exercise_config_path)

    @staticmethod
    def __now() -> datetime:
        return datetime.now(tz=pytz.UTC)

    def write_config(self, key: str, value: Any) -> None:
        # TODO: Maybe we should be updating the config object directly so re-reading
        # won't need to reload? Alternatively, maybe we should make it such that the
        # config is the config, the written variables are a separate file loaded
        raw_config = {}
        with open(self.exercise_config_path, "r") as file:
            raw_config = json.load(file)
        raw_config[key] = value
        with open(self.exercise_config_path, "w") as file:
            file.write(json.dumps(raw_config))

    def read_config(self, key: str) -> Optional[Any]:
        raw_config = {}
        with open(self.exercise_config_path, "r") as file:
            raw_config = json.load(file)
        if key not in raw_config:
            return None
        return raw_config[key]

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
