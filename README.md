# git-autograder

Git Autograder used for Git Mastery exercise solutions.

## Installation

```py
pip install git-autograder
```

## Usage

`GitAutograderRepo` initializes and reads the submission repository. It contains critical information for autograding such as the start commit (denoted by `git-mastery-start-<first commit short hash>`) and user's commits.

For basic usage, you can either initialize the `GitAutograderRepo` by declaring it as a variable:

```py
from git_autograder.repo import GitAutograderRepo

def grade():
  repo = GitAutograderRepo()
  ...
```

Or by decorating the grading function with `@autograder()` where the `GitAutograderRepo` initialization is handled by the decorator:

```py
from git_autograder.autograder import autograder

@autograder()
def grade(repo: GitAutograderRepo):
  ...
```

`GitAutograderDiffHelper` is a wrapper around the `git diff` between commits:

```py
from git_autograder.diff import GitAutograderDiffHelper

GitAutograderDiffHelper(commit_a, commit_b)
```

## Unit tests

To execute the unit tests, run `python -m pytest -s -vv`.
