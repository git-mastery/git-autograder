import os
from contextlib import contextmanager
from typing import Callable, Iterator
from unittest import mock

from git import Repo
from repo_smith.initialize_repo import RepoInitializer, initialize_repo

from git_autograder.repo import GitAutograderRepo
from git_autograder.output import GitAutograderOutput


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
    spec_path: str,
    step_id: str,
    grade_func: Callable[[GitAutograderRepo], GitAutograderOutput],
    setup: Callable[[Repo], None],
) -> Iterator[GitAutograderOutput]:
    repo_initializer = initialize_repo(spec_path)
    attach_start_tag(repo_initializer, step_id)
    with repo_initializer.initialize() as r:
        setup(r)
        autograder = GitAutograderRepo(repo_path=r.working_dir)
        result: GitAutograderOutput = grade_func(autograder)
        yield result
