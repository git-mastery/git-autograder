# AGENTS.md

Python library for autograding Git repositories, used by Git Mastery exercise repository to verify exercise solutions.

## Dev environment

- Python 3.13+
- Install dependencies: `pip install -r requirements.txt`
- Install package in dev mode: `pip install -e .`

## Testing

- Run tests: `python -m pytest -s -vv`
- Tests are located in `tests/`

## Project structure

- `src/git_autograder/` - Main package
  - `repo/` - Repository handling (GitAutograderRepo)
  - `branch.py`, `commit.py`, `remote.py` - Git object wrappers
  - `exercise.py` - Exercise configuration and grading
  - `helpers/` - Utility functions
- `docs/` - Documentation
- `tests/` - Test suite

## Code style

- **Type hints**: Required on all function signatures. Use `Optional[T]` for nullable types, union syntax `A | B` for alternatives
- **Docstrings**: Use reStructuredText format with `:param:` and `:type:` tags for public APIs
- **Imports**: Group in order: stdlib → third-party → local. Use absolute imports from `git_autograder`
- **Naming**: Classes use `GitAutograder` prefix (e.g., `GitAutograderRepo`). Private methods use single underscore prefix
- **Exceptions**: Raise `GitAutograderInvalidStateException` for invalid states, `GitAutograderWrongAnswerException` for grading failures
- **Dataclasses**: Prefer `@dataclass` for simple data containers
