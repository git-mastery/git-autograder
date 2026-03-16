import json
import subprocess
from dataclasses import dataclass
from typing import Any, Dict

from git_autograder.exception import GitAutograderInvalidStateException
from git_autograder.helpers.pr_helper.pr_helper_base import PrHelperBase
from git_autograder.pr import GitAutograderPr
from git_autograder.pr_comment import GitAutograderPrComment
from git_autograder.pr_review import GitAutograderPrReview


@dataclass(frozen=True)
class PrContext:
    pr_number: int
    pr_repo_full_name: str


class PrHelper(PrHelperBase):
    def __init__(self, context: PrContext) -> None:
        self._pr_number = context.pr_number
        self._pr_repo_full_name = context.pr_repo_full_name
        raw_data = self._fetch_pr_data()
        self._pr = self._build_pr(raw_data)

    def _fetch_pr_data(self) -> Dict[str, Any]:
        fields = [
            "number",
            "title",
            "body",
            "state",
            "author",
            "baseRefName",
            "headRefName",
            "isDraft",
            "mergedAt",
            "mergedBy",
            "latestReviews",
            "comments",
        ]
        command = [
            "gh",
            "pr",
            "view",
            str(self._pr_number),
            "--repo",
            self._pr_repo_full_name,
            "--json",
            ",".join(fields),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            stderr = result.stderr.strip() or "Unknown gh error"
            raise GitAutograderInvalidStateException(
                f"Failed to load PR #{self._pr_number} from {self._pr_repo_full_name}: {stderr}"
            )

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise GitAutograderInvalidStateException(
                "Failed to parse pull request metadata returned by GitHub CLI."
            ) from error

        if not isinstance(data, dict):
            raise GitAutograderInvalidStateException(
                "Unexpected pull request metadata shape returned by GitHub CLI."
            )
        return data

    def _build_pr(self, data: Dict[str, Any]) -> GitAutograderPr:
        latest_reviews = data.get("latestReviews") or []
        comments = data.get("comments") or []

        merged_at = data.get("mergedAt")

        return GitAutograderPr(
            number=self._pr_number,
            repo_full_name=self._pr_repo_full_name,
            title=str(data.get("title") or ""),
            body=str(data.get("body") or ""),
            state=str(data.get("state") or ""),
            author_login=(data.get("author") or {}).get("login"),
            base_branch=str(data.get("baseRefName") or ""),
            head_branch=str(data.get("headRefName") or ""),
            is_draft=bool(data.get("isDraft", False)),
            merged_at=merged_at if isinstance(merged_at, str) else None,
            merged_by_login=(data.get("mergedBy") or {}).get("login"),
            reviews=[
                GitAutograderPrReview(
                    author_login=review.get("author", {}).get("login")
                    if isinstance(review, dict)
                    else None,
                    state=review.get("state") if isinstance(review, dict) else None,
                    body=review.get("body") if isinstance(review, dict) else None,
                )
                for review in latest_reviews
                if isinstance(review, dict)
            ],
            comments=[
                GitAutograderPrComment(
                    author_login=comment.get("author", {}).get("login")
                    if isinstance(comment, dict)
                    else None,
                    body=comment.get("body") if isinstance(comment, dict) else None,
                )
                for comment in comments
                if isinstance(comment, dict)
            ],
        )

    @property
    def pr(self) -> GitAutograderPr:
        return self._pr
    