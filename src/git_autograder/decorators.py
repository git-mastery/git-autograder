import functools
import os
from datetime import datetime
from typing import Callable

import pytz

from git_autograder.exception import (
    GitAutograderInvalidStateException,
    GitAutograderWrongAnswerException,
)
from git_autograder.output import GitAutograderOutput
from git_autograder.repo import GitAutograderRepo
from git_autograder.status import GitAutograderStatus


def autograder() -> Callable[
    [Callable[..., GitAutograderOutput]], Callable[..., GitAutograderOutput]
]:
    """
    Decorator to denote that a function is an autograder function.

    Initializes the GitAutograderRepo and provides it as an argument to the function.

    Handles the Git Autograder exceptions thrown by the GitAutograderRepo or from wrong
    answers.

    All outputs are saved directly to disk.
    """

    def inner(
        func: Callable[..., GitAutograderOutput],
    ) -> Callable[..., GitAutograderOutput]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> GitAutograderOutput:
            output = None
            is_local = os.environ.get("is_local", "false") == "true"

            exercise_name = os.environ.get("exercise_name")
            if exercise_name is None:
                output = GitAutograderOutput(
                    exercise_name=None,
                    started_at=None,
                    completed_at=None,
                    is_local=is_local,
                    comments=["Missing exercise_name in environment"],
                    status=GitAutograderStatus.ERROR,
                )
                output.save()
                return output

            repo = GitAutograderRepo(is_local=is_local, exercise_name=exercise_name)
            try:
                output = func(repo, *args, **kwargs)
            except (
                GitAutograderInvalidStateException,
                GitAutograderWrongAnswerException,
            ) as e:
                output = GitAutograderOutput(
                    exercise_name=repo.exercise_name,
                    started_at=repo.started_at,
                    completed_at=datetime.now(tz=pytz.UTC),
                    is_local=repo.is_local,
                    comments=[e.message] if isinstance(e.message, str) else e.message,
                    status=(
                        GitAutograderStatus.ERROR
                        if isinstance(e, GitAutograderInvalidStateException)
                        else GitAutograderStatus.UNSUCCESSFUL
                    ),
                )
            except Exception as e:
                # Unexpected exception
                output = GitAutograderOutput(
                    exercise_name=exercise_name,
                    started_at=None,
                    completed_at=None,
                    is_local=is_local,
                    comments=[str(e)],
                    status=GitAutograderStatus.ERROR,
                )

            assert output is not None
            output.save()
            return output

        return wrapper

    return inner
