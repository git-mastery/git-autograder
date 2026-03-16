from typing import Optional

from git_autograder.role_marker import RoleMarker


class GitAutograderPrComment:
    def __init__(
        self,
        author_login: Optional[str],
        body: Optional[str],
    ) -> None:
        self._author_login = author_login
        self._body = body

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, GitAutograderPrComment):
            return False
        return (
            value.author_login == self.author_login
            and value.body == self.body
        )

    @property
    def author_login(self) -> Optional[str]:
        return self._author_login

    @property
    def body(self) -> Optional[str]:
        return self._body
    
    def is_from_user(self) -> bool:
        if self._body:
            return not RoleMarker.has_role_marker(self._body)
        # If there is no body, we can assume it's from a user.
        return True

    def is_content_equal(self, body: str) -> bool:
        return self._body.lower() == body.lower() if self._body else False
