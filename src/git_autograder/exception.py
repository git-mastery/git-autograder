import pytz
from datetime import datetime
from typing import Optional
from git_autograder.output import GitAutograderOutput
from git_autograder.status import GitAutograderStatus


class GitAutograderException(Exception):
    def __init__(
        self,
        message: str,
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

        output = GitAutograderOutput(
            exercise_name=self.exercise_name,
            started_at=self.started_at,
            completed_at=datetime.now(tz=pytz.UTC),
            is_local=self.is_local,
            comments=[message],
            status=status,
        )
        output.save()
        if self.is_local:
            print(output)


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
        message: str,
        exercise_name: str,
        started_at: datetime,
        is_local: bool,
    ) -> None:
        super().__init__(
            message,
            exercise_name,
            started_at,
            is_local,
            GitAutograderStatus.UNSUCCESSFUL,
        )
