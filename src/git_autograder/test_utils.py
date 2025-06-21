import os
import tempfile
from contextlib import ExitStack, contextmanager
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional
from unittest import mock

import pytz
from git import Repo
from repo_smith.initialize_repo import RepoInitializer, initialize_repo

from git_autograder.answers.answers import GitAutograderAnswers
from git_autograder.exception import (
    GitAutograderInvalidStateException,
    GitAutograderWrongAnswerException,
)
from git_autograder.exercise import GitAutograderExercise
from git_autograder.exercise_config import ExerciseConfig
from git_autograder.output import GitAutograderOutput
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


class GitAutograderTestLoader:
    def __init__(
        self,
        test_path: str,
        exercise_name: str,
        grade_func: Callable[[GitAutograderExercise], GitAutograderOutput],
    ) -> None:
        self.test_path = test_path
        self.exercise_name = exercise_name
        self.grade_func = grade_func

    @contextmanager
    def load(
        self,
        spec_path: str,
        step_id: str = "start",
        setup: Optional[Callable[[Repo], None]] = None,
        mock_answers: Optional[Dict[str, str]] = None,
    ) -> Iterator[GitAutograderOutput]:
        # This is done to work around the limitation of running tests not within the exercise/tests/ folder
        test_dir = os.path.dirname(self.test_path)
        spec_path = os.path.join(test_dir, spec_path)

        # We will mock all accesses to the config to avoid reading the file itself
        # Only the exercise name and repo_name matters, everything else isn't used
        repo_name = "repo"
        fake_config = ExerciseConfig(
            exercise_name=self.exercise_name,
            tags=[],
            requires_git=True,
            requires_github=True,
            base_files={},
            exercise_repo=ExerciseConfig.ExerciseRepoConfig(
                repo_type="local",
                repo_name=repo_name,
                repo_title=None,
                create_fork=None,
                init=True,
            ),
            downloaded_at=None,
        )

        answers = [(q, a) for q, a in (mock_answers or {}).items()]
        fake_answers = GitAutograderAnswers(
            questions=[v[0] for v in answers],
            answers=[v[1] for v in answers],
            validations={},
        )

        # Create a temporary folder to act as the root of the configuration
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            mock.patch(
                "git_autograder.exercise_config.ExerciseConfig.read_config",
                return_value=fake_config,
            ),
            mock.patch(
                "git_autograder.exercise.GitAutograderExercise.has_exercise_config",
                return_value=True,
            ),
            mock.patch.object(
                GitAutograderExercise, "answers", new_callable=mock.PropertyMock
            ) as mock_answers_property,
        ):
            # So within this temporary directory, you have a fake configuration and
            # fake answers if needed
            mock_answers_property.return_value = fake_answers

            # Create the solution directory named "repo" (name does not matter)
            repo_path = Path(temp_dir) / repo_name
            os.makedirs(repo_path, exist_ok=True)

            repo_initializer = initialize_repo(spec_path)
            attach_start_tag(repo_initializer, step_id)
            with repo_initializer.initialize(existing_path=str(repo_path)) as r:
                if setup is not None:
                    setup(r)

                output: Optional[GitAutograderOutput] = None
                started_at = datetime.now(tz=pytz.UTC)
                try:
                    autograder = GitAutograderExercise(exercise_path=temp_dir)
                    output = self.grade_func(autograder)
                except (
                    GitAutograderInvalidStateException,
                    GitAutograderWrongAnswerException,
                ) as e:
                    output = GitAutograderOutput(
                        exercise_name=self.exercise_name,
                        started_at=started_at,
                        completed_at=datetime.now(tz=pytz.UTC),
                        comments=[e.message]
                        if isinstance(e.message, str)
                        else e.message,
                        status=(
                            GitAutograderStatus.ERROR
                            if isinstance(e, GitAutograderInvalidStateException)
                            else GitAutograderStatus.UNSUCCESSFUL
                        ),
                    )
                except Exception as e:
                    # Unexpected exception
                    output = GitAutograderOutput(
                        exercise_name=self.exercise_name,
                        started_at=None,
                        completed_at=None,
                        comments=[str(e)],
                        status=GitAutograderStatus.ERROR,
                    )

                assert output is not None
                yield output


def assert_output(
    output: GitAutograderOutput,
    expected_status: GitAutograderStatus,
    expected_comments: List[str] = [],
) -> None:
    assert output.status == expected_status
    assert len(set(output.comments or []) & set(expected_comments)) == len(
        expected_comments
    )
