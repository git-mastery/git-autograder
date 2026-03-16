from typing import Any, List, Optional

from .pr_comment import GitAutograderPrComment
from .pr_review import GitAutograderPrReview


class GitAutograderPr:
    def __init__(
        self,
        number: int,
        repo_full_name: str,
        title: str,
        body: str,
        state: str,
        author_login: Optional[str],
        base_branch: str,
        head_branch: str,
        is_draft: bool,
        merged_at: Optional[str],
        merged_by_login: Optional[str],
        reviews: List[GitAutograderPrReview],
        comments: List[GitAutograderPrComment],
    ) -> None:
        self._number = number
        self._repo_full_name = repo_full_name
        self._title = title
        self._body = body
        self._state = state  # e.g. OPEN, CLOSED, MERGED
        self._author_login = author_login
        self._base_branch = base_branch  # Branch targeted by the PR, e.g. main
        self._head_branch = head_branch  # Branch where PR changes originate
        self._is_draft = is_draft
        self._merged_at = merged_at
        self._merged_by_login = merged_by_login
        self._reviews = reviews
        self._comments = comments

    def __eq__(self, value: Any) -> bool:
        if not isinstance(value, GitAutograderPr):
            return False
        return (
            value.number == self.number
            and value.repo_full_name == self.repo_full_name
            and value.state == self.state
        )

    @property
    def number(self) -> int:
        return self._number

    @property
    def repo_full_name(self) -> str:
        return self._repo_full_name

    @property
    def title(self) -> str:
        return self._title

    @property
    def body(self) -> str:
        return self._body

    @property
    def state(self) -> str:
        return self._state

    @property
    def author_login(self) -> Optional[str]:
        return self._author_login

    @property
    def base_branch(self) -> str:
        return self._base_branch

    @property
    def head_branch(self) -> str:
        return self._head_branch

    @property
    def is_draft(self) -> bool:
        return self._is_draft

    @property
    def merged_at(self) -> Optional[str]:
        return self._merged_at

    @property
    def merged_by_login(self) -> Optional[str]:
        return self._merged_by_login

    @property
    def reviews(self) -> List[GitAutograderPrReview]:
        return self._reviews

    @property
    def comments(self) -> List[GitAutograderPrComment]:
        return self._comments
    
    @property
    def user_reviews(self) -> List[GitAutograderPrReview]:
        return [review for review in self._reviews if review.is_from_user()]
    
    @property
    def user_comments(self) -> List[GitAutograderPrComment]:
        return [comment for comment in self._comments if comment.is_from_user()]
    
    def is_open(self) -> bool:
        return self._state.upper() == "OPEN"
    
    def is_closed(self) -> bool:
        return self._state.upper() == "CLOSED"
    
    def is_merged(self) -> bool:
        return self._state.upper() == "MERGED"