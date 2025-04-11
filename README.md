# git-autograder

Git Autograder used for Git Mastery exercise solutions.

## Installation

```py
pip install git-autograder
```

## Usage

`GitAutograderRepo` initializes and reads the submission repository. It contains critical information for autograding such as the start commit (denoted by `git-mastery-start-<first commit short hash>`) and user's commits.

For basic usage:

```py
from git_autograder import autograder, GitAutograderOutput, GitAutograderRepo

@autograder()
def grade(repo: GitAutograderRepo) -> GitAutograderOuput:
  ...
```


## Unit tests

To execute the unit tests, run `python -m pytest -s -vv`.
