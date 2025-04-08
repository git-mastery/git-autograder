from typing import List, Union


class GitAutograderException(Exception):
    def __init__(
        self,
        message: Union[str, List[str]],
    ) -> None:
        super().__init__(message)

        self.message = message


class GitAutograderInvalidStateException(GitAutograderException):
    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(message)


class GitAutograderWrongAnswerException(GitAutograderException):
    def __init__(
        self,
        comments: List[str],
    ) -> None:
        super().__init__(comments)
