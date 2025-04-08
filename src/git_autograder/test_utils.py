import os
from contextlib import contextmanager
from datetime import datetime
from typing import Callable, Iterator, Optional
from unittest import mock

import pytz
from git import Repo
from repo_smith.initialize_repo import RepoInitializer, initialize_repo

from git_autograder.exception import (
    GitAutograderInvalidStateException,
    GitAutograderWrongAnswerException,
)
from git_autograder.output import GitAutograderOutput
from git_autograder.repo import GitAutograderRepo
from git_autograder.status import GitAutograderStatus


def attach_start_tag(repo_initializer: RepoInitializer, step_id: str) -> None:
    def hook(r: Repo) -> None:
        all_commits = list(r.iter_commits())
        first_commit = list(reversed(all_commits))[0]
        first_commit_hash = first_commit.hexsha[:7]
        start_tag = f"git-mastery-start-{first_commit_hash}"
        r.create_tag(start_tag)

    repo_initializer.add_post_hook(step_id, hook)


def set_env(**kwargs) -> mock._patch_dict:
    return mock.patch.dict(os.environ, kwargs, clear=True)


@contextmanager
def setup_autograder(
    exercise_name: str,
    spec_path: str,
    step_id: str,
    grade_func: Callable[[GitAutograderRepo], GitAutograderOutput],
    setup: Callable[[Repo], None],
) -> Iterator[GitAutograderOutput]:
    repo_initializer = initialize_repo(spec_path)
    attach_start_tag(repo_initializer, step_id)
    with repo_initializer.initialize() as r:
        setup(r)
        output: Optional[GitAutograderOutput] = None
        started_at = datetime.now(tz=pytz.UTC)
        try:
            autograder = GitAutograderRepo(
                is_local=True, exercise_name=exercise_name, repo_path=r.working_dir
            )
            output = grade_func(autograder)
        except (
            GitAutograderInvalidStateException,
            GitAutograderWrongAnswerException,
        ) as e:
            output = GitAutograderOutput(
                exercise_name=exercise_name,
                started_at=started_at,
                completed_at=datetime.now(tz=pytz.UTC),
                is_local=True,
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
                is_local=True,
                comments=[str(e)],
                status=GitAutograderStatus.ERROR,
            )

        assert output is not None
        yield output
