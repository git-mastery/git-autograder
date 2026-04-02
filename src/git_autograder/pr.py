from typing import Any, Dict, List, Optional

from git import Repo
from git_autograder.commit import GitAutograderCommit
from git_autograder.exception import GitAutograderInvalidStateException
from git_autograder.pr_builders import (
    build_commits,
    build_comments,
    build_reviews,
)
from .pr_gateway import fetch_pull_request_data
from .pr_comment import GitAutograderPrComment
from .pr_review import GitAutograderPrReview


class GitAutograderPr:
    @classmethod
    def fetch(
        cls,
        pr_number: int,
        pr_repo_full_name: str,
        repo: Repo,
    ) -> "GitAutograderPr":
        data = fetch_pull_request_data(pr_number, pr_repo_full_name)
        return cls._build_from_data(pr_number, pr_repo_full_name, data, repo)

    @classmethod
    def _build_from_data(
        cls,
        pr_number: int,
        pr_repo_full_name: str,
        data: Dict[str, Any],
        repo: Repo,
    ) -> "GitAutograderPr":
        latest_reviews_data = (data.get("latestReviews") or {}).get("nodes") or []
        comments_data = (data.get("comments") or {}).get("nodes") or []
        commits = (data.get("commits") or {}).get("nodes") or []
        merged_at = data.get("mergedAt")
        created_at = data.get("createdAt")

        built_commits = build_commits(commits, repo)

        return cls(
            number=pr_number,
            repo_full_name=pr_repo_full_name,
            title=str(data.get("title") or ""),
            body=str(data.get("body") or ""),
            state=str(data.get("state") or ""),
            author_login=(data.get("author") or {}).get("login"),
            base_branch=str(data.get("baseRefName") or ""),
            head_branch=str(data.get("headRefName") or ""),
            is_draft=bool(data.get("isDraft", False)),
            merged_at=merged_at if isinstance(merged_at, str) else None,
            merged_by_login=(data.get("mergedBy") or {}).get("login"),
            created_at=created_at if isinstance(created_at, str) else None,
            commits=built_commits,
            reviews=build_reviews(latest_reviews_data),
            comments=build_comments(comments_data),
        )

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
        created_at: Optional[str],
        commits: List[GitAutograderCommit],
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
        self._created_at = created_at
        self._commits = commits
        self._reviews = reviews
        self._comments = comments
        self._user_reviews = [review for review in reviews if review.is_from_user()]
        self._user_comments = [comment for comment in comments if comment.is_from_user()]
        self._user_commits = [commit for commit in commits if commit.is_from_user()]

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
    def created_at(self) -> Optional[str]:
        return self._created_at

    @property
    def reviews(self) -> List[GitAutograderPrReview]:
        return self._reviews

    @property
    def comments(self) -> List[GitAutograderPrComment]:
        return self._comments
    
    @property
    def commits(self) -> List[GitAutograderCommit]:
        return self._commits

    @property
    def user_reviews(self) -> List[GitAutograderPrReview]:
        return self._user_reviews
    
    @property
    def user_comments(self) -> List[GitAutograderPrComment]:
        return self._user_comments
    
    @property
    def user_commits(self) -> List[GitAutograderCommit]:
        return self._user_commits
    
    @property
    def last_user_review(self) -> GitAutograderPrReview:
        if not self._user_reviews:
            raise GitAutograderInvalidStateException("No user reviews found for this PR.")
        return self._user_reviews[-1]
    
    @property
    def last_user_comment(self) -> GitAutograderPrComment:
        if not self._user_comments:
            raise GitAutograderInvalidStateException("No user comments found for this PR.")
        return self._user_comments[-1]

    @property
    def last_user_commit(self) -> GitAutograderCommit:
        if not self._user_commits:
            raise GitAutograderInvalidStateException("No user commits found for this PR.")
        return self._user_commits[-1]

    def is_open(self) -> bool:
        return self._state.upper() == "OPEN"
    
    def is_closed(self) -> bool:
        return self._state.upper() == "CLOSED"
    
    def is_merged(self) -> bool:
        return self._state.upper() == "MERGED"