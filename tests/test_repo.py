import os
from unittest import mock

from git import Repo
from repo_smith.initialize_repo import RepoInitializer, initialize_repo

from src.git_autograder.repo import GitAutograderRepo


def set_env(**kwargs) -> mock._patch_dict:
    return mock.patch.dict(os.environ, kwargs, clear=True)


def attach_start_tag(repo_initializer: RepoInitializer, step_id: str) -> None:
    def hook(r: Repo) -> None:
        all_commits = list(r.iter_commits())
        first_commit = list(reversed(all_commits))[0]
        first_commit_hash = first_commit.hexsha[:7]
        start_tag = f"git-mastery-start-{first_commit_hash}"
        r.create_tag(start_tag)

    repo_initializer.add_post_hook(step_id, hook)


@set_env(repository_name="mock")
def test_repo_initialization_no_is_local() -> None:
    repo_initializer = initialize_repo("tests/specs/no_local.yml")
    attach_start_tag(repo_initializer, "commit")
    with repo_initializer.initialize() as r:
        repo = GitAutograderRepo(repo_path=r.working_dir)
        assert not repo.__is_local
