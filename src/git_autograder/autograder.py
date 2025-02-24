import functools
from typing import Callable, TypeVar
from git_autograder.repo import GitAutograderRepo

R = TypeVar("R")


def autograder() -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator to denote that a function is an autograder function.

    Initializes the GitAutograderRepo and provides it as an argument to the function.
    """

    def inner(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> R:
            repo = GitAutograderRepo()
            return func(repo, *args, **kwargs)

        return wrapper

    return inner
