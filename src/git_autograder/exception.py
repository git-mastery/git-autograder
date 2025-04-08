from datetime import datetime
from typing import List, Optional, Union

from git_autograder.status import GitAutograderStatus


class GitAutograderException(Exception):
    def __init__(
        self,
        message: Union[str, List[str]],
        exercise_name: Optional[str],
        started_at: Optional[datetime],
        is_local: Optional[bool],
        status: GitAutograderStatus,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.exercise_name = exercise_name
        self.started_at = started_at
        self.is_local = is_local
        self.status = status


class GitAutograderInvalidStateException(GitAutograderException):
    def __init__(
        self,
        message: str,
        exercise_name: Optional[str],
        started_at: Optional[datetime],
        is_local: Optional[bool],
    ) -> None:
        super().__init__(
            message,
            exercise_name,
            started_at,
            is_local,
            GitAutograderStatus.ERROR,
        )


class GitAutograderWrongAnswerException(GitAutograderException):
    def __init__(
        self,
        comments: List[str],
        exercise_name: Optional[str],
        started_at: datetime,
        is_local: bool,
    ) -> None:
        super().__init__(
            comments,
            exercise_name,
            started_at,
            is_local,
            GitAutograderStatus.UNSUCCESSFUL,
        )
